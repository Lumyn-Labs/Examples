package frc.robot;

import static edu.wpi.first.units.Units.Meters;
import static edu.wpi.first.units.Units.MetersPerSecond;

import com.lumynlabs.connection.usb.USBPort;
import com.lumynlabs.devices.ConnectorXAnimate;
import com.lumynlabs.domain.config.ConfigBuilder;
import com.lumynlabs.domain.led.Animation;
import com.lumynlabs.domain.led.DirectLED;

import edu.wpi.first.units.Units;
import edu.wpi.first.units.measure.Distance;
import edu.wpi.first.wpilibj.AddressableLEDBuffer;
import edu.wpi.first.wpilibj.LEDPattern;
import edu.wpi.first.wpilibj.util.Color;
import edu.wpi.first.wpilibj.util.Color8Bit;
import frc.robot.Robot;

public class LEDSystem {


  private final ConnectorXAnimate m_leds = new ConnectorXAnimate();

  private static final Color kPrimary = new Color(new Color8Bit(255, 153, 28));

  private static final String kDirectLedZone = "left-side";
  private static final int kDirectLedLength = 30;

  private DirectLED m_directLed;
  private AddressableLEDBuffer m_directLedBuffer;
  private boolean m_directLedEnabled = false;

  private static final Distance kLedSpacing = Meters.of(1.0 / 120.0);
  private final LEDPattern mRainbow = LEDPattern.rainbow(255, 128);
  private final LEDPattern mScrollingRainbow = mRainbow.scrollAtAbsoluteSpeed(MetersPerSecond.of(0.1), kLedSpacing);

    public void initializeLEDs(){
        m_leds.Connect(USBPort.kUSB1);
        if (Robot.isSimulation()) {
        m_leds.ApplyConfiguration(buildConfig());
        }

        m_directLedBuffer = new AddressableLEDBuffer(kDirectLedLength);
        m_directLed = m_leds.leds.createDirectLED(kDirectLedZone, kDirectLedLength);
    }

    private com.lumynlabs.domain.config.LumynDeviceConfig buildConfig() {
        return new ConfigBuilder()
            .forTeam("3481")
            // Channels
            .addChannel(1, "backLights", 30)
                .addStripZone("left-side", 30, false)
                .addStripZone("right-side", 30, false)
            .endChannel()
            
            
            
            // Groups
            .addGroup("backLights").addZone("left-side").addZone("right-side").endGroup()
            
            // Sequences
            .addSequence("celebrate")
                .addStep("RainbowCycle").withDelay(50).withRepeat(10).endStep()
                .addStep("Fire").withColor(255, 153, 28).withDelay(100).withRepeat(10).endStep()
            .endSequence()
            
            
            .build();
    }

  public void disableInitLEDS(){
    m_leds.leds.SetGroupAnimationSequence("backLights", "celebrate");
  }
  public void autoInitLEDS(){
         // Play a rainbow animation on the "front" zone
        m_leds.leds.SetAnimation(Animation.Fire)
        .ForGroup("backLights")
        .WithColor(kPrimary)
        .WithDelay(Units.Milliseconds.of(100))
        .RunOnce(false);
  }

  public void teleopInitLEDS(){
    
     m_leds.leds.SetAnimation(Animation.Comet)
        .ForGroup("backLights")
        .WithColor(kPrimary)
        .WithDelay(Units.Milliseconds.of(100))
        .RunOnce(false);
  }
  public void intakeLEDS(){
    
     m_leds.leds.SetAnimation(Animation.Blink)
        .ForGroup("backLights")
        .WithColor(Color.kBlue)
        .WithDelay(Units.Milliseconds.of(20))
        .RunOnce(false);
  }

  public void RainbowLEDCycle(){
      
    m_leds.leds.SetAnimation(Animation.RainbowRoll)
        .ForGroup("backLights")
        .WithColor(kPrimary)
        .WithDelay(Units.Milliseconds.of(40))
        .RunOnce(false);
  
  }
}
