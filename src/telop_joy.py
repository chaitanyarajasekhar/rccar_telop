#! /usr/bin/python
import psutil
import rospy
import subprocess, os, signal

from std_msgs.msg import Float64
from sensor_msgs.msg import Joy

def terminate_process_and_children(p):
    process = psutil.Process(p.pid)
    for sub_process in process.children(recursive=True):
        sub_process.send_signal(signal.SIGINT)
    p.wait()  # we wait for children to terminate
    #p.terminate()

class CarTelop:

    def __init__(self):
        ''' '''

        # VESC publishers intialization
        self.pub_steer    = rospy.Publisher("commands/servo/position",Float64, queue_size = 100)
        self.pub_throttle = rospy.Publisher("commands/motor/duty_cycle", Float64, queue_size = 100)
        self.pub_speed    = rospy.Publisher("commands/motor/speed", Float64, queue_size = 100)
        self.joy0_sub     = rospy.Subscriber("/j0/joy", Joy, self.joyListenerCallback)

        # intialze steering value
        steering_angle = 0.5
        rospy.loginfo(steering_angle)
        self.pub_steer.publish(steering_angle)

        # setting up the recording for the rosbag
        self.command = "rosbag record /rgb/image_raw_color /commands/motor/duty_cycle /commands/servo/position /commands/motor/duty_cycle"
        self.rosbag_rec = False

        rospy.loginfo("intializing")
        # waiting to make sure the all the processes start
        rate = rospy.Rate(2)
        rate.sleep()
        rate.sleep()

        self.rcCarTelop()


    def rcCarTelop(self):
        '''  '''
        # changing rate
        rate = rospy.Rate(10)
        rospy.loginfo("starting")

        while not rospy.is_shutdown():
            rate.sleep()


    def joyListenerCallback(self,data):

        acc_multiplier_1 = 1
        acc_multiplier_2 = 1

        if data.buttons[6] == 1:
            # acceleration  multiplier
            acc_multiplier_1 = 5
        if data.buttons[4] == 1:
            # acceleration  multiplier
            acc_multiplier_2 = 2
        if data.buttons[0] == 1 and self.rosbag_rec == False:
            # start recording the bags
            rospy.loginfo("start recording the bag file")
            self.rosbag_process = subprocess.Popen(self.command,shell=True, stdout=subprocess.PIPE)
            self.rosbag_rec = True
        if data.buttons[3] == 1 and self.rosbag_rec == True:
            # reset car and stop recording
            # intialze steering value
            # steering_angle = 0.5
            # #rospy.loginfo("steering_angle = 0")
            # self.pub_steer.publish(steering_angle)
            # # stoping the car
            # #rospy.loginfo("speed = 0")
            # self.pub_speed.publish(0)
            # # terminate the rosbag collection
            rospy.loginfo("terminating recording the bag file")
            terminate_process_and_children(self.rosbag_process)
            self.rosbag_rec = False
        if data.buttons[1] == 1:
            # stop and reset car
            # intialze steering value
            steering_angle = 0.5
            # rospy.loginfo("steering_angle = 0")
            self.pub_steer.publish(steering_angle)
            # stoping the car
            # rospy.loginfo("speed = 0")
            self.pub_speed.publish(0)

        duty_cycle_value = 0.1 * data.axes[1] * acc_multiplier_1 * acc_multiplier_2
        steering_value   = 0.5 - 0.4 * data.axes[2]

        log_text = "steering_angle = " + str(steering_value) + " throttle_value = " + \
                    str(duty_cycle_value)

        # rospy.loginfo(log_text)
        self.pub_throttle.publish(duty_cycle_value)
        self.pub_steer.publish(steering_value)


if __name__=='__main__':
    try:
        # init ros node
        rospy.init_node('rc_car_telop')
        car_telop = CarTelop()
    except rospy.ROSInterruptException:
        pass
