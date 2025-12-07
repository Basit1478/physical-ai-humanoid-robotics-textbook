---
sidebar_position: 1
title: "Introduction to ROS 2 Architecture"
---

# Introduction to ROS 2 Architecture

## Learning Outcomes
By the end of this chapter, you should be able to:
- Explain the fundamental concepts of ROS 2
- Describe the architecture of ROS 2 systems
- Understand the differences between ROS 1 and ROS 2
- Identify the key components of a ROS 2 system

## Table of Contents
- [Introduction to ROS 2](#introduction-to-ros-2)
- [Architecture Overview](#architecture-overview)
- [Nodes and Communication](#nodes-and-communication)
- [Practical Examples](#practical-examples)
- [Summary](#summary)

## Introduction to ROS 2

ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It is a collection of tools, libraries, and conventions that aim to simplify the task of creating complex and robust robot behavior across a wide variety of robot platforms.

### Key Features of ROS 2
- **Distributed computing**: Multiple processes can run on different machines
- **Language independence**: Support for multiple programming languages
- **Real-time support**: Enhanced real-time capabilities
- **Security**: Built-in security features
- **Quality of Service (QoS)**: Configurable communication policies

## Architecture Overview

The ROS 2 architecture is built on top of DDS (Data Distribution Service), which provides a middleware layer for communication between different components.

### Core Components
```
┌─────────────────┐    ┌─────────────────┐
│   Node A        │    │   Node B        │
├─────────────────┤    ├─────────────────┤
│ Publishers      │    │ Subscribers     │
│ Services        │    │ Services        │
│ Actions         │    │ Actions         │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                DDS Layer
```

The architecture diagram above shows how nodes communicate through the DDS middleware layer. Nodes can contain publishers, subscribers, services, and actions that enable different types of communication patterns.

### DDS Implementation
ROS 2 uses DDS as its communication middleware, which provides:
- Publish/Subscribe communication pattern
- Request/Reply communication pattern
- Discovery services
- Quality of Service (QoS) policies

## Nodes and Communication

### Nodes
A node is an executable that uses ROS 2 to communicate with other nodes. Nodes are the basic building blocks of a ROS 2 system.

### Communication Patterns
ROS 2 supports three main communication patterns:

1. **Publish/Subscribe**: One-way communication from publisher to subscriber
2. **Service/Client**: Request/reply communication pattern
3. **Action**: Goal-based communication with feedback and status

### Example Code Structure
```
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class MinimalPublisher : public rclcpp::Node
{
public:
  MinimalPublisher()
  : Node("minimal_publisher"), count_(0)
  {
    publisher_ = this->create_publisher<std_msgs::msg::String>("topic", 10);
    timer_ = this->create_wall_timer(
      500ms, std::bind(&MinimalPublisher::timer_callback, this));
  }

private:
  void timer_callback()
  {
    auto message = std_msgs::msg::String();
    message.data = "Hello, world! " + std::to_string(count_++);
    RCLCPP_INFO(this->get_logger(), "Publishing: '%s'", message.data.c_str());
    publisher_->publish(message);
  }
  rclcpp::TimerBase::SharedPtr timer_;
  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  size_t count_;
};
```

## Practical Examples

### Creating a Simple Publisher Node
1. Create a new ROS 2 package
2. Implement a publisher node that sends messages
3. Configure the node with appropriate QoS settings
4. Test the communication between nodes

### Quality of Service (QoS) Settings
QoS policies allow you to configure how messages are delivered:
- Reliability: Best effort or reliable delivery
- Durability: Volatile or transient local
- History: Keep last N messages or keep all messages

## Summary

This chapter introduced the fundamental concepts of ROS 2 architecture. You learned about the key components, communication patterns, and how nodes interact through the DDS middleware. The next chapter will dive deeper into ROS 2 nodes and communication patterns.