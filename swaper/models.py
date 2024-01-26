from typing import Any
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models.deletion import SET_NULL



###########################
# TrueKinetix Base Models #
###########################

class CoreModule(models.Model):
    """ Pi/Core module """

    # Unique hardware ID is a 96 bit field formatted as a 24 char hex string
    hardware_id = models.CharField(
        max_length=24,
        primary_key=True,
        verbose_name=_('Unique hardware ID'))

    firmware = models.CharField(
        max_length=32, default=None, null=True, blank=True,
        verbose_name=_('Firmware Version')
    )

    bootloader = models.CharField(
        max_length=32, default=None, null=True, blank=True,
        verbose_name=_('Bootloader Version')
    )

    # Voltage divider calibration
    # conversion factor
    v0Conv = models.FloatField(
        null=False, default=108, verbose_name=_('v0Conv'),
        help_text=_('Voltage 0 conversion')
    )

    v1Conv = models.FloatField(
        null=False, default=35.5, verbose_name=_('v1Conv'),
        help_text=_('Voltage 1 conversion')
    )

    v2Conv = models.FloatField(
        null=False, default=71, verbose_name=_('v2Conv'),
        help_text=_('Voltage 2 conversion')
    )

    is_deleted = models.BooleanField(
        verbose_name=_('Deleted'),
        default=False
    )

    created_at = models.DateTimeField(
        auto_now=True
    )

    def is_valid(self):
        return len(self.hardware_id) == 24 and self.hardware_id != 'ffffffffffffffffffffffff'

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = 'tk_core_module'
        verbose_name = _('Pi/Core Module')


class Bike(models.Model):
    """ Bike data """

    DEVICE_TYPE_NONE = 0
    DEVICE_TYPE_BIKE = 1
    DEVICE_TYPE_TRAINER = 2
    DEVICE_TYPES = {
        DEVICE_TYPE_NONE: _('Unknown device'),
        DEVICE_TYPE_BIKE: _('TrueBike'),
        DEVICE_TYPE_TRAINER: _('Trainer'),
    }

    # Device type and subtype from Capability value
    # see fixtures/capabilities.json
    CAPABILITY_DEVICE_TYPE = 'DEVICE_TYPE'
    CAPABILITY_DEVICE_SUBTYPE = 'DEVICE_SUBTYPE'

    PROCESSOR_TYPE_RASPBERRYPI = "Cortex-A53"
    PROCESSOR_TYPE_BANANAPI = "Cortex-A7"

    # Hardware Pi/Core module is swappable
    core_module = models.OneToOneField(
        CoreModule, on_delete=SET_NULL,
        null=True, default=None, blank=True, db_index=True)

    tk_bike_id = models.IntegerField(
        null=False, verbose_name=_('Bike ID'),
        help_text=_('TrueKinetix bike id'), unique=True, db_index=True)

    # device type such as TrueBike, Trainer
    device_type = models.SmallIntegerField(
        verbose_name=_("Device Type"),
        choices=[(k, v) for k, v in DEVICE_TYPES.items()],
        default=0,
        help_text='Device type is set from License Capability',
    )

    sensorData = models.TextField(
        null=True, blank=True, verbose_name=_('TbSensor'),
        help_text=_('TB Sensor data'), unique=False, db_index=False)

    created_at = models.DateTimeField(auto_now=True)

    @property
    def tk_hw_id(self):
        """ Pi/Core hardware ID """
        if self.core_module:
            return self.core_module.pk
        return None

    @property
    def valid_sensor_data(self):
        """
            Return sensorData only if it passes some simple validation
        """
        return self.sensorData

    @property
    def core_bootloader(self):
        """ The bootloader version of the installed core module """
        if self.core_module:
            return self.core_module.bootloader
        return None

    @property
    def core_firmware(self):
        """ The firmware version of the installed core module """
        if self.core_module:
            return self.core_module.firmware
        return None

    def __str__(self):
        """ Display name for the model """
        device_type = self.DEVICE_TYPES.get(self.device_type, self._meta.verbose_name)
        return f'{device_type} #{self.tk_bike_id}'

    class Meta:
        db_table = 'tk_bike'
        verbose_name = _('Bike')

###########################
# Swaper Classes          #
###########################
   
# swaper class manage the swap of a field 
# it has 4 main properties :
#   - to_swap: holds an  object to be updated 
#   - swap_with : hold an objet providing the value to  use for the swap update
#   - swapState: hold an integer that represent the state of the swap
#      the state value can be :
#         swapState == -1  : not done    
#         swapState == 0 : done / no error
#         swapState >= 1 : failed / error          
#   - SWAPPABLE : a list of object property that are allowed to be swapped     

class Swaper ():
    # small additional structure for easying swapstate usage and value
    class SwapState:    
        TODO=-1                       
        DONE=0                       
        FAILED=1                   
    # ---------------- // SwapState //

    ERROR = False  # True or a message when swap error, False otherwise
    swap_state = SwapState.TODO # state and return value of the swap process, default -1/todo
    SWAPPABLE = [Bike.core_module]  # TO DO: add a check that the value being swapped is part of this list   
    SWAP = [Bike.core_module]
    to_swap = Bike | None
    swap_with = Bike | CoreModule | None  
    
    
    # While the 'dbentry_newcore_add' and/or 'dbentry_oldcore_del' options
    # are not activated (see DB behaviour settings form controls of the
    # html form from templates/list_all.html, the html form submition data 
    # processed in the views.update() method in views.py) 
  
    def do_swap (self):
        # Check swaper is set correcly
        if self.can_do_swap() != True:
            return self.swap_state
            
        bikePrev_core = self.to_swap.core_module
        new_core = None
        isBike = True
        # if we have a coremodule we grab the linked bike first
        if type(self.swap_with) is CoreModule:            
            bikeToUse = Bike.objects.get(core_module_id=self.swap_with.hardware_id)            
            
            if bikeToUse is not None and bikeToUse.core_module.hardware_id == self.swap_with.hardware_id:
                self.swap_with = bikeToUse
            else:
                # we proceed the case the new coremodule has no bike 
                isBike = False
                new_core =  self.swap_with
            
        # swap start here...
        if isBike == True:
            new_core = self.swap_with.core_module
        
        # we get ride of the links and db unicity constraints 
        self.to_swap.core_module = None
        self.to_swap.save()
        
        if isBike == True:
            self.swap_with.core_module = None
            self.swap_with.save()
        
        # now we can switch the bikes and their core modules 
        # update to_swap
        self.to_swap.core_module = new_core
       
        # update swap_with
        if isBike == True:
            self.swap_with.core_module = bikePrev_core
        # save changes in the db
        try:
            self.to_swap.save()
            if isBike == True:
                self.swap_with.save()
            return self.swap_state
        
        except:
            self.set_error('error on save()')
            return self.swap_state
      
    def reset_state (self):
        self.swap_state = self.SwapState.TODO 
        self.ERROR = False

    def set_error (self, message = True):
        self.swap_state = self.SwapState.FAILED 
        self.ERROR = message
        return self.swap_state
    
    def can_do_swap (self):
        # Check swaper is set correcly
        if self.swap_state > self.SwapState.TODO:
            self.set_error("swap state must be reset")
            return False
        if self.to_swap is None or self.swap_with is None:
            self.set_error("Swapping elements are missing (swapWith or toSwap)")
            return False
        # TO DO: add missing/other checks
        return True

"""
About the do_swap() method :
 
Data used to do a swap must meet the following conditions:
  - exist as 2 hardware ids in the DB in prior to the swap process:
  - be row entries in the hardware table   
  - be set as ForeignKey of valid row entriess in the bike table
  - the following assertion:
    (tk_core_module.hardware_id == DB.tk_bike.core_module_id) 
    must be True for both hardware id 
    Note that is only for swap WITHOUT the previously mentioned options 
"""