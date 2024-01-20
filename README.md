# DjangoApp_valueSwaper" 


## "Convention" 
consistent swaper class method and properties names to help understand and specify the swap settings.


### Example
A generic swap is made of 2 components. 

    - "TO Swap" :  component value "requesting" an update using the same type of value from another similar component 
    - "Swap WITH", the component providing the "new" value(s) for the "TO Swap" component.

Note about the similarity of value types and components:
Using same types is not mandatory but provide a way to insure compatibility of the data, maintain consistency through updates resulting in higher success rates.

### Use Case: Bike coremodule replacement 

A Bike with id Bike_001 and a core module with id CoreMod_hwd001. This core module have to be replaced by  another hardware.
The replacement is made using the hardware from another Bike, such as, the new core module is with the hardware id CoreMod_ha005 and come from the Bike with id Bike_008.

Before replacement:
    - Bike_001 -> CoreMod_hwd001
    - Bike_008 -> CoreMod_hwd003
After replacenent:
    - Bike_001 -> CoreMod_hwd003
    - Bike_008 -> CoreMod_hwd001

The Swaper will be set like using a BikeIdSwap object like: 
    - To Swap: Bike_001 
    - Swap WITH: Bike_008
    - SWAP : Bike.core_module

    in the code :
    /* instanciate a Swaper object */
    swaper = Swaper()   
    /* set the 'to_swao' and 'swap_with' properties of        the Swaper object */
    swaper.to_swap = Bike_001
    swaper.swap_with = Bike_008
    /* set the SWAP property list if needed  */
    swaper.SWAP = [Bike.core_module] /* actually the default */
    /* trigger the value swap */
    swaper.do_swap()

After the swap :
    - Bike_001 -> CoreMod_hwd003
    - Bike_008 -> CoreMod_hwd001