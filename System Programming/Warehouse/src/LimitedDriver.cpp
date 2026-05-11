#include <vector>
#include <string>
#include <iostream>
#include <cstdio>
#include "../include/Volunteer.h"
#include "../include/Order.h"

LimitedDriverVolunteer::LimitedDriverVolunteer(int id, const string &name, int maxDistance, int distancePerStep, int maxOrders) : DriverVolunteer(id, name, maxDistance, distancePerStep), maxOrders(maxOrders), ordersLeft(maxOrders) {}

LimitedDriverVolunteer *LimitedDriverVolunteer::clone() const
{
    return new LimitedDriverVolunteer(*this);
}

int LimitedDriverVolunteer::getMaxOrders() const
{
    return maxOrders;
}

int LimitedDriverVolunteer::getNumOrdersLeft() const
{
    return ordersLeft;
}

bool LimitedDriverVolunteer::hasOrdersLeft() const
{
    return ordersLeft > 0;
}

bool LimitedDriverVolunteer::canTakeOrder(const Order &order) const
{
    return !isBusy() & (getMaxDistance() >= order.getOrderDistance()) & hasOrdersLeft();
}

void LimitedDriverVolunteer::acceptOrder(const Order &order)
{
    activeOrderId = order.getId();
    setDistanceLeft(order);
    ordersLeft--;
}

string LimitedDriverVolunteer::toString() const
{
    char buffer[100];
    std::sprintf(buffer, "volunteer %s limited_driver %d %d %d", getName().c_str(), getMaxDistance(), getDistancePerStep(), getMaxOrders());
    string res = buffer;
    return res;
}

string LimitedDriverVolunteer::type() const{
    return "LimitedDriver";
}