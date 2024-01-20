# DjangoApp_valueSwaper" 


## "Convention" 
consistent swaper class method and properties names to help understand and specify the swap settings.

### Example
A generic swap is made of 2 components. 

    - "TO Swap" :  component value "requesting" an update using the same type of value from another similar component 
    - "Swap FROM", the component providing the "new" value(s) for the "TO Swap" component.

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
    - Swap From: Bike_008

    in the code :
    /* instanciate a BikeIdSwap object */
    swapValue = ValueSwap()  
    /* set the 'to_swao' and 'swap_from' properties of        the valueSwap object */
    swapValue.to_swap = Bike_001
    swapValue.swap_from = Bike_008
    /* instanciate a Swaper object */
    swaper = Swaper() 
    /* set the swapping property using the swapValue object */
    swaper.swapping = swapValue.do_swap()

After the swap :

bike1  ### B_A->ha_3 
bike2  ### B_C->ha_1    - Bike_001 -> CoreMod_hwd001
    - Bike_008 -> CoreMod_hwd003