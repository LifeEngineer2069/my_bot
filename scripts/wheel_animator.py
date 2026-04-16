#!/usr/bin/env python3
"""
wheel_animator.py

Dead-reckons wheel joint positions from cmd_vel so RViz shows realistic
wheel rotation when running on the real robot without encoders.

Replaces joint_state_broadcaster in real-robot mode (which would only
publish zeros since there is no encoder feedback).
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState

WHEEL_RADIUS     = 0.0425  # m — must match my_controller.yaml wheel_radius
WHEEL_SEPARATION = 0.184   # m — must match my_controller.yaml wheel_separation
PUBLISH_HZ       = 50.0    # match diff_cont publish_rate


class WheelAnimator(Node):
    def __init__(self):
        super().__init__('wheel_animator')

        self.declare_parameter('odom_scale', 1.0)
        self._scale = self.get_parameter('odom_scale').value

        self._left_pos  = 0.0
        self._right_pos = 0.0
        self._v_left    = 0.0
        self._v_right   = 0.0
        self._last_time = self.get_clock().now()

        self.create_subscription(
            Twist,
            '/diff_cont/cmd_vel_unstamped',
            self._cmd_cb,
            10,
        )

        self._pub = self.create_publisher(JointState, '/joint_states', 10)
        self.create_timer(1.0 / PUBLISH_HZ, self._publish_cb)

    def _cmd_cb(self, msg: Twist):
        lin = msg.linear.x * self._scale
        ang = msg.angular.z * self._scale
        self._v_left  = (lin - ang * WHEEL_SEPARATION / 2.0) / WHEEL_RADIUS
        self._v_right = (lin + ang * WHEEL_SEPARATION / 2.0) / WHEEL_RADIUS

    def _publish_cb(self):
        now = self.get_clock().now()
        dt  = (now - self._last_time).nanoseconds * 1e-9
        self._last_time = now

        self._left_pos  += self._v_left  * dt
        self._right_pos += self._v_right * dt

        js = JointState()
        js.header.stamp = now.to_msg()
        js.name         = ['left_wheel_joint', 'right_wheel_joint']
        js.position     = [self._left_pos,  self._right_pos]
        js.velocity     = [self._v_left,    self._v_right]
        self._pub.publish(js)


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(WheelAnimator())
    rclpy.shutdown()


if __name__ == '__main__':
    main()
