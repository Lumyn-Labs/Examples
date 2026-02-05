# Examples

This repository contains examples that demonstrate how to use Lumyn Labs devices with WPILib. Each example is fully functional and can be run in simulation or on a real robot. Both Java and C++ implementations are provided with identical functionality.

## Controls

The examples use an Xbox controller to trigger different effects:

| Button | Effect |
|--------|--------|
| A | Chase animation on climbers |
| B | Fire animation on left climber |
| X | Rainbow cycle on climbers |
| Y | Scrolling "GO TEAM!" text on matrices |
| LB | Sparkle animation on climbers |
| RB | Heartbeat animation on climbers |
| LT | Play "celebrate" sequence |
| RT | Play image sequence on front matrix |
| Start | Set climbers and matrices to primary color |
| Back | Turn off climbers and matrices |
| RS | Toggle DirectLED rainbow on left climber |

## Running on Hardware

When running on a real robot, you will need a ConnectorX Animate device and a config.json file that matches the simulation configuration. The examples use a configuration with two LED strips (60 LEDs total for "climbers") and two LED matrices (16x16 and 8x32).

In order to use the image sequences on a real robot, you will need to copy the contents of the deploy/connectorx directory to the root of your ConnectorX Animate device's SD card.
