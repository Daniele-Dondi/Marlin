# Syringebot Lab Robot Firmware
 
Based on a DerAndere project 
repository [DerAndere1/Marlin at https://github.com](https://github.com/DerAndere1/Marlin/tree/Marlin2ForPipetBot), the [Wiki](https://github.com/DerAndere1/Marlin/wiki)
or on the [PipetBot-A8 project homepage](https://derandere.gitlab.io/pipetbot-a8) 
.
This project is intended for a syringebot robot for liquid handling for driving chemical reactions.
The current version supports up to 6 syringes.
For each syringe two servocontrolled valves drive the liquids inside a reaction vessel that is thermocontrolled with PID. 
The current version supports and is tested only on the Megatronics v.3 board.
![Megatronics 3 pic](https://github.com/Daniele-Dondi/Marlin/blob/SyringeBot/img/megatronics-board.jpg?raw=true)

## Marlin2ForPipetBot Branch

__Not for production use. Use with caution!__

Whitelist (Gcodes tested and working)

G1 [Xx.xxxx] [Yy.yyyy] [Zz.zzzz] [Ii.iiii] [Jj.jjjj] [Kk.kkkk] [Ee.eeee] [Ff.ffff]

G28 [X] [Y] [Z] [I] [J] [K]

M280 (servo control)

M140 (set bed temperature)

M104 (set hotend temperature)

M301 (set hotend PID parameters)

M304 (set bed PID parameters)

M400 (wait for all moves to finish)

## Configuration

Configuration is done by editing the file Marlin/Configuration.h. 


`NON_E_AXES`: 
The number of axes that are not used for extruders (axes that
benefit from endstops and homing). 

Allowed values: [5, 6]

Regardless of the settings, firmware-internal axis names are
I (AXIS4), J (AXIS5), K (AXIS6).



## Hardware Abstraction Layer (HAL)

Marlin 2.0 introduces a layer of abstraction so that all the existing high-level code can be built for 32-bit platforms while still retaining full 8-bit AVR compatibility. Retaining AVR compatibility and a single code-base is important to us, because we want to make sure that features and patches get as much testing and attention as possible, and that all platforms always benefit from the latest improvements.

### Current HALs

  name|processor|speed|flash|sram|logic|fpu
  ----|---------|-----|-----|----|-----|---
  [Arduino AVR](https://www.arduino.cc/)|ATmega, ATTiny, etc.|16-20MHz|64-256k|2-16k|5V|no
  [Teensy++ 2.0](http://www.microchip.com/wwwproducts/en/AT90USB1286)|[AT90USB1286](http://www.microchip.com/wwwproducts/en/AT90USB1286)|16MHz|128k|8k|5V|no
  [Arduino STM32](https://github.com/rogerclarkmelbourne/Arduino_STM32)|[STM32F1](https://www.st.com/en/microcontrollers-microprocessors/stm32f103.html) ARM-Cortex M3|72MHz|256-512k|48-64k|3.3V|no
  [Due](https://www.arduino.cc/en/Guide/ArduinoDue), [RAMPS-FD](http://www.reprap.org/wiki/RAMPS-FD), etc.|[SAM3X8E ARM-Cortex M3](http://www.microchip.com/wwwproducts/en/ATsam3x8e)|84MHz|512k|64+32k|3.3V|no
  [Re-ARM](https://www.kickstarter.com/projects/1245051645/re-arm-for-ramps-simple-32-bit-upgrade)|[LPC1768 ARM-Cortex M3](http://www.nxp.com/products/microcontrollers-and-processors/arm-based-processors-and-mcus/lpc-cortex-m-mcus/lpc1700-cortex-m3/512kb-flash-64kb-sram-ethernet-usb-lqfp100-package:LPC1768FBD100)|100MHz|512k|32+16+16k|3.3-5V|no
  [MKS SBASE](http://forums.reprap.org/read.php?13,499322)|LPC1768 ARM-Cortex M3|100MHz|512k|32+16+16k|3.3-5V|no
  [Azteeg X5 GT](https://www.panucatt.com/azteeg_X5_GT_reprap_3d_printer_controller_p/ax5gt.htm)|LPC1769 ARM-Cortex M3|120MHz|512k|32+16+16k|3.3-5V|no
  [Selena Compact](https://github.com/Ales2-k/Selena)|LPC1768 ARM-Cortex M3|100MHz|512k|32+16+16k|3.3-5V|no
  [Teensy 3.5](https://www.pjrc.com/store/teensy35.html)|ARM-Cortex M4|120MHz|512k|192k|3.3-5V|yes
  [Teensy 3.6](https://www.pjrc.com/store/teensy36.html)|ARM-Cortex M4|180MHz|1M|256k|3.3V|yes

### HALs in Development

  name|processor|speed|flash|sram|logic|fpu
  ----|---------|-----|-----|----|-----|---
  [STEVAL-3DP001V1](http://www.st.com/en/evaluation-tools/steval-3dp001v1.html)|[STM32F401VE Arm-Cortex M4](http://www.st.com/en/microcontrollers/stm32f401ve.html)|84MHz|512k|64+32k|3.3-5V|yes
  [Smoothieboard](http://reprap.org/wiki/Smoothieboard)|LPC1769 ARM-Cortex M3|120MHz|512k|64k|3.3-5V|no
  [Adafruit Grand Central M4](https://www.adafruit.com/product/4064)|ARM-Cortex M4|120MHz|1M|256k|3.3V|yes

## Submitting Patches

Proposed patches should be submitted as a Pull Request against the [SyringeBot](https://github.com/Daniele-Dondi/Marlin/tree/SyringeBot) branch.

- Follow the [Coding Standards](http://marlinfw.org/docs/development/coding_standards.html) to gain points with the maintainers.

### [RepRap.org Wiki Page](http://reprap.org/wiki/Marlin)

## Credits

The current Marlin dev team consists of:

 - Scott Lahteine [[@thinkyhead](https://github.com/thinkyhead)] - USA &nbsp; [![Flattr Scott](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=thinkyhead&url=https://github.com/MarlinFirmware/Marlin&title=Marlin&language=&tags=github&category=software)
 - Roxanne Neufeld [[@Roxy-3D](https://github.com/Roxy-3D)] - USA
 - Bob Kuhn [[@Bob-the-Kuhn](https://github.com/Bob-the-Kuhn)] - USA
 - Chris Pepper [[@p3p](https://github.com/p3p)] - UK
 - João Brazio [[@jbrazio](https://github.com/jbrazio)] - Portugal
 - Erik van der Zalm [[@ErikZalm](https://github.com/ErikZalm)] - Netherlands &nbsp; [![Flattr Erik](http://api.flattr.com/button/flattr-badge-large.png)](https://flattr.com/submit/auto?user_id=ErikZalm&url=https://github.com/MarlinFirmware/Marlin&title=Marlin&language=&tags=github&category=software)

Marlin2ForPipetBot is modified by:

 - DerAndere [[@DerAndere1](https://github.com/DerAndere1)] - Germany
 - Garbriel Beraldo [@GabrielBeraldo](https://github.com/GabrielBeraldo)] - Brasil
 - Olivier Briand [@hobiseven](https://github.com/hobiseven)] - France
 - Wolverine [@MohammadSDGHN](https://github.com/MohammadSDGHN) - Undisclosed 
 - bilsef [@bilsef](https://github.com/bilsef) - Undisclosed 
 - FNeo31 [@FNeo31](https://github.com/FNeo31) - Undisclosed 
 
Marlin for Syringebot is modified by:
 - Daniele Dondi - Italy

## License

Syringebot is published under the [GPL license](https://github.com/DerAndere1/Marlin/blob/Marlin2ForPipetBot/LICENSE) because we believe in open development. The GPL comes with both rights and obligations. Whether you use Marlin firmware as the driver for your open or closed-source product, you must keep Marlin open, and you must provide your compatible Marlin source code to end users upon request. The most straightforward way to comply with the Marlin license is to make a fork of Marlin on Github, perform your modifications, and direct users to your modified fork.

While we can't prevent the use of this code in products (3D printers, CNC, etc.) that are closed source or crippled by a patent, we would prefer that you choose another firmware or, better yet, make your own.
