#include <vector>
#include <string>
#include "../include/Volunteer.h"
#include "../include/Order.h"

LimitedDriverVolunteer::LimitedDriverVolunteer(int id, const string &name, int maxDistance, int distancePerStep, int maxOrders) : DriverVolunteer(id,name,maxDistance,distancePerStep), maxOrders(maxOrders), ordersLeft(maxOrders){}

LimitedDriverVolunteer *LimitedDriverVolunteer::clone() const{
    return new LimitedDriverVolunteer(*this);
}

int LimitedDriverVolunteer::getMaxOrders() const{
    return maxOrders;
}

int LimitedDriverVolunteer::getNumOrdersLeft() const{
    return ordersLeft;
}

bool LimitedDriverVolunteer::hasOrdersLeft() const{
    return ordersLeft>0;
}

bool LimitedDriverVolunteer::canTakeOrder(const Order &order) const{
    return !isBusy() & getMaxDistance() >= order.getOrderDistance() & hasOrdersLeft();
}

void LimitedDriverVolunteer::acceptOrder(const Order &order) {
    activeOrderId=order.getId();
    setDistanceLeft(order);
    ordersLeft--;
}
//need to implement toString()