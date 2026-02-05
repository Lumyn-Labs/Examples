// Copyright (c) Lumyn Labs. All Rights Reserved.
// Licensed under the MIT License. See LICENSE in the project root.

package frc.robot;

import com.lumynlabs.connection.usb.USBPort;
import com.lumynlabs.devices.ConnectorXAnimate;
import com.lumynlabs.domain.config.ConfigBuilder;
import com.lumynlabs.domain.led.Animation;
import com.lumynlabs.domain.led.DirectLED;
import com.lumynlabs.domain.led.MatrixTextScrollDirection;

import edu.wpi.first.units.Units;
import edu.wpi.first.units.measure.Distance;
import edu.wpi.first.wpilibj.AddressableLEDBuffer;
import edu.wpi.first.wpilibj.LEDPattern;
import edu.wpi.first.wpilibj.TimedRobot;
import edu.wpi.first.wpilibj.XboxController;
import edu.wpi.first.wpilibj.util.Color;
import edu.wpi.first.wpilibj.util.Color8Bit;

import static edu.wpi.first.units.Units.Meters;
import static edu.wpi.first.units.Units.MetersPerSecond;

/**
 * Lumyn Labs ConnectorXAnimate Demo
 */
public class Robot extends TimedRobot {

  private final ConnectorXAnimate m_leds = new ConnectorXAnimate();
  private final XboxController m_controller = new XboxController(0);

  private static final Color kPrimary = new Color(new Color8Bit(0, 100, 255));
  private static final Color kSecondary = new Color(new Color8Bit(255, 200, 0));
  private static final Color kAccent = new Color(new Color8Bit(255, 255, 255));

  private static final String kDirectLedZone = "left-climber";
  private static final int kDirectLedLength = 30;

  private DirectLED m_directLed;
  private AddressableLEDBuffer m_directLedBuffer;
  private boolean m_directLedEnabled = false;

  private static final Distance kLedSpacing = Meters.of(1.0 / 120.0);
  private final LEDPattern mRainbow = LEDPattern.rainbow(255, 128);
  private final LEDPattern mScrollingRainbow = mRainbow.scrollAtAbsoluteSpeed(MetersPerSecond.of(0.1), kLedSpacing);

  private boolean m_lastA, m_lastB, m_lastX, m_lastY;
  private boolean m_lastLB, m_lastRB, m_lastLT, m_lastRT;
  private boolean m_lastStart, m_lastBack;
  private boolean m_lastRS;

  @Override
  public void robotInit() {
    m_leds.Connect(USBPort.kUSB1);
    if (isSimulation()) {
      m_leds.ApplyConfiguration(buildConfig());
    }

    m_directLedBuffer = new AddressableLEDBuffer(kDirectLedLength);
    m_directLed = m_leds.leds.createDirectLED(kDirectLedZone, kDirectLedLength);
  }

  private com.lumynlabs.domain.config.LumynDeviceConfig buildConfig() {
    return new ConfigBuilder()
        .forTeam("9999")
        // Channels
        .addChannel(1, "climbers", 60)
            .addStripZone("left-climber", 30, false)
            .addStripZone("right-climber", 30, true)
        .endChannel()
        
        .addChannel(2, "front", 256)
            .addMatrixZone("front-matrix", 16, 16)
        .endChannel()
        
        .addChannel(3, "back", 256)
            .addMatrixZone("back-matrix", 8, 32)
        .endChannel()
        
        // Groups
        .addGroup("climbers").addZone("left-climber").addZone("right-climber").endGroup()
        .addGroup("matrices").addZone("front-matrix").addZone("back-matrix").endGroup()
        
        // Sequences
        .addSequence("celebrate")
            .addStep("RainbowCycle").withDelay(10).withRepeat(3).endStep()
            .addStep("Confetti").withColor(255, 215, 0).withDelay(30).withRepeat(5).endStep()
            .addStep("Blink").withColor(0, 255, 0).withDelay(200).withRepeat(4).endStep()
        .endSequence()
        
        // Bitmaps
        .addBitmap("Heart")
            .animated("heart_16x16", 100)
        .endBitmap()
        
        .build();
  }

  @Override
  public void robotPeriodic() {
    if (m_directLedEnabled && m_directLed != null && m_directLedBuffer != null) {
      mScrollingRainbow.applyTo(m_directLedBuffer);
      m_directLed.update(m_directLedBuffer);
    }
  }

  @Override
  public void disabledInit() {
  m_leds.leds.SetAnimation(Animation.Breathe)
    .ForGroup("climbers").WithColor(kPrimary).WithDelay(Units.Milliseconds.of(5)).RunOnce(false);
    m_leds.leds.SetText("").ForZone("front-matrix").RunOnce(true);
  }

  @Override
  public void autonomousInit() {
    m_leds.leds.SetAnimation(Animation.Comet)
        .ForGroup("climbers").WithColor(color(138, 43, 226)).WithDelay(Units.Milliseconds.of(50)).RunOnce(false);
    m_leds.leds.SetText("AUTO")
        .ForZone("front-matrix").WithColor(kSecondary).WithDirection(MatrixTextScrollDirection.Left)
        .WithDelay(Units.Milliseconds.of(100)).RunOnce(false);
  }

  @Override
  public void teleopInit() {
  m_leds.leds.SetAnimation(Animation.Breathe)
    .ForGroup("climbers").WithColor(kPrimary).WithDelay(Units.Milliseconds.of(5)).RunOnce(false);
    m_leds.leds.SetText("").ForZone("front-matrix").RunOnce(true);
  }

  @Override
  public void teleopPeriodic() {
    
    if (pressed(m_controller.getAButton(), m_lastA)) {
      m_leds.leds.SetAnimation(Animation.Chase)
          .ForGroup("climbers").WithColor(kPrimary).WithDelay(Units.Milliseconds.of(40)).RunOnce(false);
    }
    m_lastA = m_controller.getAButton();

    
    if (pressed(m_controller.getBButton(), m_lastB)) {
      m_leds.leds.SetAnimation(Animation.Fire)
          .ForZone("left-climber").WithColor(color(255, 35, 0)).WithDelay(Units.Milliseconds.of(40)).RunOnce(false);
    }
    m_lastB = m_controller.getBButton();

    
    if (pressed(m_controller.getXButton(), m_lastX)) {
    m_leds.leds.SetAnimation(Animation.RainbowCycle)
      .ForGroup("climbers").WithDelay(Units.Milliseconds.of(10)).RunOnce(false);
    }
    m_lastX = m_controller.getXButton();

    
    if (pressed(m_controller.getYButton(), m_lastY)) {
      m_leds.leds.SetText("GO TEAM!")
          .ForGroup("matrices").WithColor(kSecondary).WithDirection(MatrixTextScrollDirection.Left)
          .WithDelay(Units.Milliseconds.of(80)).RunOnce(false);
    }
    m_lastY = m_controller.getYButton();

    
    if (pressed(m_controller.getLeftBumperButton(), m_lastLB)) {
      m_leds.leds.SetAnimation(Animation.Sparkle)
          .ForGroup("climbers").WithColor(kAccent).WithDelay(Units.Milliseconds.of(100)).RunOnce(false);
    }
    m_lastLB = m_controller.getLeftBumperButton();

    
    if (pressed(m_controller.getRightBumperButton(), m_lastRB)) {
      m_leds.leds.SetAnimation(Animation.Heartbeat)
          .ForGroup("climbers").WithColor(color(255, 0, 50)).WithDelay(Units.Milliseconds.of(30)).RunOnce(false);
    }
    m_lastRB = m_controller.getRightBumperButton();

    
    boolean lt = m_controller.getLeftTriggerAxis() > 0.5;
    if (pressed(lt, m_lastLT)) {
      m_leds.leds.SetAnimationSequence("front-matrix", "celebrate");
      m_leds.leds.SetGroupAnimationSequence("climbers", "celebrate");
    }
    m_lastLT = lt;

    
    boolean rt = m_controller.getRightTriggerAxis() > 0.5;
    if (pressed(rt, m_lastRT)) {
      m_leds.leds.SetImageSequence("robot")
          .ForZone("front-matrix").WithColor(kPrimary).SetColor(false).RunOnce(false);
    }
    m_lastRT = rt;

    
    if (pressed(m_controller.getStartButton(), m_lastStart)) {
      m_leds.leds.SetGroupColor("climbers", kPrimary);
      m_leds.leds.SetGroupColor("matrices", kPrimary);
    }
    m_lastStart = m_controller.getStartButton();

    
    if (pressed(m_controller.getBackButton(), m_lastBack)) {
      m_leds.leds.SetGroupColor("climbers", new Color(0, 0, 0));
      m_leds.leds.SetGroupColor("matrices", new Color(0, 0, 0));
    }
    m_lastBack = m_controller.getBackButton();

    if (pressed(m_controller.getRightStickButton(), m_lastRS)) {
      m_directLedEnabled = !m_directLedEnabled;
      if (!m_directLedEnabled && m_directLed != null) {
        m_directLed.reset();
      }
    }
    m_lastRS = m_controller.getRightStickButton();
  }

  private static boolean pressed(boolean current, boolean last) { return current && !last; }
  private static Color color(int r, int g, int b) { return new Color(new Color8Bit(r, g, b)); }

  @Override public void disabledPeriodic() {}
  @Override public void autonomousPeriodic() {}
  @Override public void testInit() {}
  @Override public void testPeriodic() {}
  @Override public void simulationInit() {}
  @Override public void simulationPeriodic() {}
}
