// Copyright (c) Lumyn Labs. All Rights Reserved.
// Licensed under the MIT License. See LICENSE in the project root.

#include "Robot.h"

#include <frc/RobotBase.h>
#include <units/time.h>

#include <lumyn/connection/USBPort.h>

void Robot::RobotInit() {
  m_leds.Connect(lumyn::connection::USBPort::kUSB1);
  if (frc::RobotBase::IsSimulation()) {
    ApplyConfig();
  }
}

void Robot::ApplyConfig() {
  lumyn::config::ConfigBuilder builder;
  auto config = builder
      .ForTeam("9999")

  // Channels
      .AddChannel("climbers", 60)
          .AddStripZone("left-climber", 30, false)
          .AddStripZone("right-climber", 30, true)
          .EndChannel()

      
      .AddChannel("front", 256)
          .AddMatrixZone("front-matrix", 16, 16)
          .EndChannel()

      
      .AddChannel("back", 256)
          .AddMatrixZone("back-matrix", 8, 32)
          .EndChannel()

  // Groups
      .AddGroup("climbers").AddZone("left-climber").AddZone("right-climber").EndGroup()
      .AddGroup("matrices").AddZone("front-matrix").AddZone("back-matrix").EndGroup()
      .AddGroup("all")
          .AddZone("left-climber").AddZone("right-climber")
          .AddZone("front-matrix").AddZone("back-matrix")
          .EndGroup()

  // Sequences
      .AddSequence("celebrate")
          .AddStep("RainbowCycle").WithDelay(10).WithRepeat(3).EndStep()
          .AddStep("Confetti").WithColor(255, 215, 0).WithDelay(30).WithRepeat(5).EndStep()
          .AddStep("Blink").WithColor(0, 255, 0).WithDelay(200).WithRepeat(4).EndStep()
          .EndSequence()

  // Bitmaps
      .AddBitmap("Heart")
          .Animated("heart_16x16", 100)
          .EndBitmap()

      .Build();

  m_leds.ApplyConfiguration(config);
}

void Robot::DisabledInit() {
  m_leds.SetAnimation(lumyn::led::Animation::Breathe)
      .ForGroup("all").WithColor(kPrimary).WithDelay(5_ms).RunOnce(false);
  m_leds.SetText("").ForZone("front-matrix").RunOnce(true);
}

void Robot::AutonomousInit() {
  m_leds.SetAnimation(lumyn::led::Animation::Comet)
      .ForGroup("climbers").WithColor(Color8(138, 43, 226)).WithDelay(50_ms).RunOnce(false);
  m_leds.SetText("AUTO")
      .ForZone("front-matrix").WithColor(kSecondary)
      .WithDirection(lumyn::internal::Command::LED::MatrixTextScrollDirection::LEFT)
      .WithDelay(100_ms).RunOnce(false);
}

void Robot::TeleopInit() {
  m_leds.SetAnimation(lumyn::led::Animation::Breathe)
      .ForGroup("all").WithColor(kPrimary).WithDelay(5_ms).RunOnce(false);
  m_leds.SetText("").ForZone("front-matrix").RunOnce(true);
}

void Robot::TeleopPeriodic() {
  
  if (Pressed(m_controller.GetAButton(), m_lastA)) {
    m_leds.SetAnimation(lumyn::led::Animation::Chase)
        .ForGroup("climbers").WithColor(kPrimary).WithDelay(40_ms).RunOnce(false);
  }
  m_lastA = m_controller.GetAButton();

  
  if (Pressed(m_controller.GetBButton(), m_lastB)) {
    m_leds.SetAnimation(lumyn::led::Animation::Fire)
        .ForZone("left-climber").WithColor(Color8(255, 35, 0)).WithDelay(40_ms).RunOnce(false);
  }
  m_lastB = m_controller.GetBButton();

  
  if (Pressed(m_controller.GetXButton(), m_lastX)) {
    m_leds.SetAnimation(lumyn::led::Animation::RainbowCycle)
        .ForGroup("all").WithDelay(10_ms).RunOnce(false);
  }
  m_lastX = m_controller.GetXButton();

  
  if (Pressed(m_controller.GetYButton(), m_lastY)) {
    m_leds.SetText("GO TEAM!")
        .ForGroup("matrices").WithColor(kSecondary)
        .WithDirection(lumyn::internal::Command::LED::MatrixTextScrollDirection::LEFT)
        .WithDelay(80_ms).RunOnce(false);
  }
  m_lastY = m_controller.GetYButton();

  
  if (Pressed(m_controller.GetLeftBumper(), m_lastLB)) {
    m_leds.SetAnimation(lumyn::led::Animation::Sparkle)
        .ForGroup("climbers").WithColor(kAccent).WithDelay(100_ms).RunOnce(false);
  }
  m_lastLB = m_controller.GetLeftBumper();

  
  if (Pressed(m_controller.GetRightBumper(), m_lastRB)) {
    m_leds.SetAnimation(lumyn::led::Animation::Heartbeat)
        .ForGroup("climbers").WithColor(Color8(255, 0, 50)).WithDelay(30_ms).RunOnce(false);
  }
  m_lastRB = m_controller.GetRightBumper();

  
  bool lt = m_controller.GetLeftTriggerAxis() > 0.5;
  if (Pressed(lt, m_lastLT)) {
    m_leds.SetAnimationSequence("front-matrix", "celebrate");
    m_leds.SetGroupAnimationSequence("climbers", "celebrate");
  }
  m_lastLT = lt;

  
  bool rt = m_controller.GetRightTriggerAxis() > 0.5;
  if (Pressed(rt, m_lastRT)) {
    m_leds.SetImageSequence("robot")
        .ForZone("front-matrix").WithColor(kPrimary).SetColor(false).RunOnce(false);
  }
  m_lastRT = rt;

  
  if (Pressed(m_controller.GetStartButton(), m_lastStart)) {
    m_leds.SetGroupColor("all", kPrimary);
  }
  m_lastStart = m_controller.GetStartButton();

  
  if (Pressed(m_controller.GetBackButton(), m_lastBack)) {
    m_leds.SetGroupColor("all", frc::Color{0, 0, 0});
  }
  m_lastBack = m_controller.GetBackButton();
}

#ifndef RUNNING_FRC_TESTS
int main() { return frc::StartRobot<Robot>(); }
#endif
