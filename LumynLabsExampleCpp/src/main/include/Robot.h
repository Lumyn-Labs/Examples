// Copyright (c) Lumyn Labs. All Rights Reserved.
// Licensed under the MIT License. See LICENSE in the project root.

#pragma once

#include <array>
#include <memory>

#include <frc/AddressableLED.h>
#include <frc/LEDPattern.h>
#include <frc/TimedRobot.h>
#include <frc/XboxController.h>
#include <frc/util/Color.h>
#include <units/length.h>
#include <units/velocity.h>

#include <lumyn/device/ConnectorXAnimate.h>
#include <lumyn/device/DirectLED.h>
#include <lumyn/configuration/ConfigBuilder.h>
#include <lumyn/led/Animation.h>

/**
 * Lumyn Labs ConnectorXAnimate Demo
 */
class Robot : public frc::TimedRobot {
 public:
  void RobotInit() override;
  void RobotPeriodic() override;

  void DisabledInit() override;
  void DisabledPeriodic() override {}

  void AutonomousInit() override;
  void AutonomousPeriodic() override {}

  void TeleopInit() override;
  void TeleopPeriodic() override;

  void TestInit() override {}
  void TestPeriodic() override {}

  void SimulationInit() override {}
  void SimulationPeriodic() override {}

 private:
  void ApplyConfig();

  lumyn::device::ConnectorXAnimate m_leds;
  frc::XboxController m_controller{0};

  static constexpr auto kPrimary = frc::Color{0.0, 0.392, 1.0};
  static constexpr auto kSecondary = frc::Color{1.0, 0.784, 0.0};
  static constexpr auto kAccent = frc::Color{1.0, 1.0, 1.0};

  static constexpr const char* kDirectLedZone = "left-climber";
  static constexpr int kDirectLedLength = 30;

  std::array<frc::AddressableLED::LEDData, kDirectLedLength> m_directLedBuffer;
  std::unique_ptr<lumyn::device::DirectLED> m_directLed;
  bool m_directLedEnabled = false;

  static constexpr units::meter_t kLedSpacing{1.0 / 120.0};
  frc::LEDPattern m_rainbow = frc::LEDPattern::Rainbow(255, 128);
  frc::LEDPattern m_scrollingRainbow = m_rainbow.ScrollAtAbsoluteSpeed(0.1_mps, kLedSpacing);

  bool m_lastA{}, m_lastB{}, m_lastX{}, m_lastY{};
  bool m_lastLB{}, m_lastRB{}, m_lastLT{}, m_lastRT{};
  bool m_lastStart{}, m_lastBack{};
  bool m_lastRS{};

  static frc::Color Color8(int r, int g, int b) { return {r / 255.0, g / 255.0, b / 255.0}; }
  static bool Pressed(bool current, bool last) { return current && !last; }
};
