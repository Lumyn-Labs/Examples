// Copyright (c) Lumyn Labs. All Rights Reserved.
// Licensed under the MIT License. See LICENSE in the project root.

#pragma once

#include <frc/TimedRobot.h>
#include <frc/XboxController.h>
#include <frc/util/Color.h>

#include <lumyn/device/ConnectorXAnimate.h>
#include <lumyn/configuration/ConfigBuilder.h>
#include <lumyn/led/Animation.h>

/**
 * Lumyn Labs ConnectorXAnimate Demo
 */
class Robot : public frc::TimedRobot {
 public:
  void RobotInit() override;
  void RobotPeriodic() override {}

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

  
  bool m_lastA{}, m_lastB{}, m_lastX{}, m_lastY{};
  bool m_lastLB{}, m_lastRB{}, m_lastLT{}, m_lastRT{};
  bool m_lastStart{}, m_lastBack{};

  static frc::Color Color8(int r, int g, int b) { return {r / 255.0, g / 255.0, b / 255.0}; }
  static bool Pressed(bool current, bool last) { return current && !last; }
};
