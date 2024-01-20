from django.contrib import messages
from django.http import HttpResponse, Http404
from .models import CoreModule, Bike, Swaper, BikeIdSwap
from django.template import loader 
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

# swaper app index/home page  url@/
def index(request):
    bikes = Bike.objects.all() 
    coreModules = CoreModule.objects.all()
 
    context = {
        "bikes": bikes,
        "coremodules": coreModules,
        "bikeValues": bikes.values()
    }
    template = loader.get_template("swaper_index.html")
    return HttpResponse(template.render(context, request))
  
def details(request):

    # the submitted data can be either:
    # a coremoduleid or a bikei
    # we prefer to use the bikeids to ref data, 
    # when coremoduleid are used we 1rst try to retrieve the linked bikeid   
      
    coreid = request.GET.get('coremoduleid')
    bikeid = request.GET.get('bikeid')
    bikes = Bike.objects.all()
    coreModules = CoreModule.objects.all() 

    selectedCore = None
    selectedBike =  None
    
    if coreid is None and bikeid is None:
        messages.error(request, _('No ids provided.'))
        return redirect('/swaper')
    
    if len(coreid) > 0:
        selectedCore = CoreModule.objects.get(hardware_id = coreid)
        selectedBike = Bike.objects.get(tk_bike_id = selectedCore.bike.tk_bike_id)
 
    elif len(bikeid) > 0:
        selectedBike = Bike.objects.get (tk_bike_id = bikeid)
        selectedCore = CoreModule.objects.get(hardware_id = selectedBike.core_module.hardware_id)
    
    if selectedBike is None  or  selectedBike is Bike.DoesNotExist:
        selectedBike = Bike()
        selectedBike.tk_hw_id = coreid
        selectedBike.core_module = selectedCore
        
    context = {
        'selected': selectedBike,
        'bikes' : bikes,
        'hardwares' : coreModules
    }

    return render(request, 'list_all.html', context)


def update(request):
   
    swapvalues = BikeIdSwap()
    
    bikeidselectd = request.GET.get('selectedbikeid')
    prevcoreid = request.GET.get('selectedbikeid_coremoduleid')
    newcoreid = request.GET.get('newbikecoremoduleid')
    addNewCore = False # request.GET.get ('dbentry_newcore_add')
    delOldCore = False # request.GET.get ('dbentry_oldcore_del')
    swapOldCore = True# request.GET.get ('dbentry_oldcore_upd')
    selectedBike = Bike.objects.get(tk_bike_id=bikeidselectd)

    if selectedBike.tk_hw_id != prevcoreid or selectedBike.tk_hw_id == newcoreid: 
        messages.error(request, _('the actual core module id is not consistent with the retrieved data, the db might already be updated or else, restart the process from start, if the issue persist check the value directly in the database to help debug.'))
        return redirect('/swaper')
   
    swapWith = CoreModule.objects.get(hardware_id=newcoreid)
     
    if swapWith is None:
        # TO DO: 
        # option 'addNewCore' to add support for new hardware
        # (not in the database) and proceed a commit of the new hardware,
        # as an additional optional step part of the swap update                   
        # if addNewCore == 'checked':
        #    messages.info(request, _('the new core module is not in the database.'))
        # else:
        messages.error (request, _('the new core module is not in the database.'))
        return redirect('/swaper')

    # start swap   
    swapvalues.to_swap = selectedBike
    swapvalues.swap_with = swapWith

    swaper = Swaper()
    swaper.swapping = swapvalues
    if swaper.can_do_swap() is False:
        messages.error (request, _(swaper.ERROR))
        return redirect('/swaper')
    
    elif swaper.do_swap() is False:
        messages.error (request, _(swaper.ERROR))
        return redirect('/swaper')
    
    else:
        messages.success(request, _('Bike successfully updated.'))
        queryString = '/swaper/details/?coremoduleid=' + newcoreid + '&bikeid=' + bikeidselectd
        return redirect(queryString)