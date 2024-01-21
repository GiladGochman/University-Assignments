#include <vector>
#include <string>
#include "../include/Volunteer.h"
#include "../include/Order.h"

LimitedCollectorVolunteer::LimitedCollectorVolunteer(int id, string name, int coolDown, int maxOrders) : CollectorVolunteer(id, name, coolDown), maxOrders(maxOrders), ordersLeft(maxOrders){}

LimitedCollectorVolunteer *LimitedCollectorVolunteer:: clone() const{
    return new LimitedCollectorVolunteer(*this);
}

bool LimitedCollectorVolunteer:: hasOrdersLeft() const{
    return ordersLeft > 0; 
}

bool LimitedCollectorVolunteer::canTakeOrder(const Order &order) const {
    if(isBusy() | !hasOrdersLeft()) return false;
    return true;
}

void LimitedCollectorVolunteer::acceptOrder(const Order &order) {
    activeOrderId = order.getId();
    setTimeLeft();
    ordersLeft--;  
}

int LimitedCollectorVolunteer::getMaxOrders() const{
    return maxOrders;
}

int LimitedCollectorVolunteer::getNumOrdersLeft() const{
    return ordersLeft;
}
//NEED TO IMPLEMENT TOSTRING()
