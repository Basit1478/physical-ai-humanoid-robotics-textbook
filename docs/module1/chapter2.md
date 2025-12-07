---
sidebar_position: 2
title: "ROS 2 Nodes and Communication Patterns"
---

# ROS 2 Nodes and Communication Patterns

## Learning Outcomes
By the end of this chapter, you should be able to:
- Create and manage ROS 2 nodes
- Implement different communication patterns (publish/subscribe, service/client, action)
- Configure Quality of Service (QoS) settings
- Debug common communication issues

## Table of Contents
- [Understanding ROS 2 Nodes](#understanding-ros-2-nodes)
- [Publish/Subscribe Pattern](#publishsubscribe-pattern)
- [Service/Client Pattern](#serviceclient-pattern)
- [Action Pattern](#action-pattern)
- [Quality of Service (QoS)](#quality-of-service-qos)
- [Practical Examples](#practical-examples)
- [Summary](#summary)

## Understanding ROS 2 Nodes

A ROS 2 node is a process that performs computation. Nodes are the fundamental building blocks of a ROS 2 system. Each node is designed to perform a specific task and communicates with other nodes through topics, services, and actions.

### Node Lifecycle
```
┌─────────────────┐
│   Unconfigured  │
└─────────┬───────┘
          │ create()
          ▼
┌─────────────────┐
│    Inactive     │
└─────────┬───────┘
          │ activate()
          ▼
┌─────────────────┐
│     Active      │ ←─── execute()
└─────────┬───────┘
          │ deactivate()
          ▼
┌─────────────────┐
│    Inactive     │
└─────────┬───────┘
          │ cleanup()
          ▼
┌─────────────────┐
│   Unconfigured  │
└─────────────────┘
```

The diagram above illustrates the lifecycle of a ROS 2 node, showing the different states and transitions between them. This lifecycle management allows for more robust and configurable systems.

### Creating a Node
Nodes are typically created by inheriting from the Node class provided by the client library (rclcpp for C++ or rclpy for Python).

## Publish/Subscribe Pattern

The publish/subscribe pattern is the most common communication method in ROS 2. It enables asynchronous one-way communication between nodes.

### Publishers and Subscribers
- **Publisher**: Sends messages to a topic
- **Subscriber**: Receives messages from a topic
- **Topic**: Named channel for message exchange

### Example Implementation
```cpp
// Publisher
auto publisher = this->create_publisher<std_msgs::msg::String>("topic_name", 10);

// Subscriber
auto subscription = this->create_subscription<std_msgs::msg::String>(
    "topic_name",
    10,
    [this](const std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "I heard: '%s'", msg->data.c_str());
    });
```

## Service/Client Pattern

The service/client pattern provides synchronous request/reply communication between nodes.

### Services and Clients
- **Service**: Provides a function that can be called by clients
- **Client**: Calls a service and waits for the response

### Example Implementation
```cpp
// Service Server
auto service = this->create_service<example_interfaces::srv::AddTwoInts>(
    "add_two_ints",
    [this](
        const example_interfaces::srv::AddTwoInts::Request::SharedPtr request,
        example_interfaces::srv::AddTwoInts::Response::SharedPtr response) {
        response->sum = request->a + request->b;
        RCLCPP_INFO(this->get_logger(), "Incoming request: %ld + %ld = %ld",
                    request->a, request->b, response->sum);
    });

// Client
auto client = this->create_client<example_interfaces::srv::AddTwoInts>("add_two_ints");
```

## Action Pattern

Actions provide goal-based communication with feedback and status updates, suitable for long-running tasks.

### Action Components
- **Goal**: Request to perform an action
- **Feedback**: Periodic updates during action execution
- **Result**: Final outcome of the action

### Example Implementation
```cpp
// Action Server
auto action_server = rclcpp_action::create_server<action_tutorials_interfaces::action::Fibonacci>(
    this->get_node_base_interface(),
    this->get_node_clock_interface(),
    this->get_node_logging_interface(),
    this->get_node_waitables_interface(),
    "fibonacci",
    std::bind(&MinimalActionServer::handle_goal, this, _1, _2),
    std::bind(&MinimalActionServer::handle_cancel, this, _1),
    std::bind(&MinimalActionServer::handle_accepted, this, _1));
```

## Quality of Service (QoS)

QoS settings allow fine-tuning of communication behavior to meet specific requirements.

### QoS Policies
- **Reliability**: Guarantees message delivery
  - `RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT`: Try to deliver messages, but don't guarantee
  - `RMW_QOS_POLICY_RELIABILITY_RELIABLE`: Guarantee delivery of messages

- **Durability**: Determines if late-joining subscribers receive past messages
  - `RMW_QOS_POLICY_DURABILITY_VOLATILE`: Only receive messages sent after subscription
  - `RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL`: Receive past and future messages

- **History**: How many messages to store
  - `RMW_QOS_POLICY_HISTORY_KEEP_LAST`: Store the most recent N messages
  - `RMW_QOS_POLICY_HISTORY_KEEP_ALL`: Store all messages

### QoS Profile Examples
```cpp
// Reliable communication with keep-all history
rclcpp::QoS qos_profile(10);
qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_RELIABLE);
qos_profile.durability(RMW_QOS_POLICY_DURABILITY_TRANSIENT_LOCAL);
qos_profile.history(RMW_QOS_POLICY_HISTORY_KEEP_ALL);

// Best-effort communication with keep-last history
rclcpp::QoS qos_sensor(10);
qos_profile.reliability(RMW_QOS_POLICY_RELIABILITY_BEST_EFFORT);
qos_profile.durability(RMW_QOS_POLICY_DURABILITY_VOLATILE);
qos_profile.history(RMW_QOS_POLICY_HISTORY_KEEP_LAST);
```

## Practical Examples

### Example 1: Simple Publisher-Subscriber
1. Create a publisher node that sends sensor data
2. Create a subscriber node that processes the data
3. Configure appropriate QoS settings for sensor data

### Example 2: Service-Based Communication
1. Implement a service that calculates robot path
2. Create a client that requests path calculations
3. Handle service calls asynchronously

### Example 3: Action-Based Navigation
1. Create an action server for robot navigation
2. Implement goal execution with feedback
3. Handle preemption and cancellation

## Summary

This chapter covered the core communication patterns in ROS 2: publish/subscribe, service/client, and action patterns. You learned how to implement each pattern and configure Quality of Service settings to meet specific requirements. The next chapter will explore implementation patterns and best practices.