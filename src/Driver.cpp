#include <vector>
#include <string>
#include <iostream>
#include <cstdio>
#include "../include/Volunteer.h"
#include "../include/Order.h"

DriverVolunteer::DriverVolunteer(int id, string name, int maxDistance, int distancePerStep) : Volunteer(id, name), maxDistance(maxDistance), distancePerStep(distancePerStep), distanceLeft(0) {}

DriverVolunteer *DriverVolunteer::clone() const
{
    return new DriverVolunteer(*this);
}

int DriverVolunteer::getDistanceLeft() const
{
    return distanceLeft;
}

int DriverVolunteer::getMaxDistance() const
{
    return maxDistance;
}

int DriverVolunteer::getDistancePerStep() const
{
    return distancePerStep;
}

bool DriverVolunteer::decreaseDistanceLeft()
{
    distanceLeft = distanceLeft - distancePerStep;
    if (distanceLeft <= 0)
    {
        distanceLeft = 0;
        return true;
    }
    return false;
}

bool DriverVolunteer::hasOrdersLeft() const
{
    return true;
}

bool DriverVolunteer::canTakeOrder(const Order &order) const
{
    return (!isBusy() & getMaxDistance() >= order.getOrderDistance());
}

void DriverVolunteer::acceptOrder(const Order &order)
{
    activeOrderId = order.getId();
    distanceLeft = order.getOrderDistance();
}

void DriverVolunteer::setDistanceLeft(const Order &order)
{
    distanceLeft = order.getOrderDistance();
}

void DriverVolunteer::step()
{
    if (!isBusy())
        return;
    if (decreaseDistanceLeft())
    {
        completedOrderId = activeOrderId;
        activeOrderId = NO_ORDER;
    }
}

string DriverVolunteer::toString() const
{
    char buffer[100];
    std::sprintf(buffer, "volunteer %s driver %d %d", getName().c_str(), getMaxDistance(), getDistancePerStep());
    string res = buffer;
    return res;
}

// NEED TO IMPLEMENT TOSTRING()
