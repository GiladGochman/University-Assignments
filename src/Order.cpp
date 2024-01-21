#include <string>
#include <vector>
#include "../include/Order.h"
using std::string;
using std::vector;

Order::Order(int id, int customerId, int distance): id(id), customerId(customerId), distance(distance), status(OrderStatus(0)), collectorId(NO_VOLUNTEER), driverId(NO_VOLUNTEER){}

int Order::getId() const{
    return id;
}

int Order::getCustomerId() const{
    return customerId;
}

int Order::getCollectorId() const{
    return collectorId;
}

int Order::getDriverId() const{
    return driverId;
}

int Order::getOrderDistance() const{
    return distance;
}

OrderStatus Order::getStatus() const{
    return status;
}

void Order::setStatus(OrderStatus status){
    this->status = status;
}

void Order::setCollectorId(int collectorId){
    this->collectorId = collectorId;
}

void Order::setDriverId(int driverId){
    this->driverId = driverId;
}

const string Order::toString() const{
    return "order "+customerId;
}
//need to implement toString()