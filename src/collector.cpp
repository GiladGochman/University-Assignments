#include <vector>
#include <string>
#include "../include/Volunteer.h"
#include "../include/Order.h"

CollectorVolunteer::CollectorVolunteer(int id, string name, int coolDown) : Volunteer(id,name), coolDown(coolDown), timeLeft(0) {}

CollectorVolunteer *CollectorVolunteer::clone() const{
    return new CollectorVolunteer(*this);
}

int CollectorVolunteer::getCoolDown() const{
    return coolDown;
}

int CollectorVolunteer::getTimeLeft() const{
    return timeLeft;
}

bool CollectorVolunteer::decreaseCoolDown() {
    if(timeLeft>0){
        timeLeft = timeLeft - 1;
        return true;
    }
    return false;

}

bool CollectorVolunteer::canTakeOrder(const Order &order) const{
    if(isBusy()) return false;
    return true;

}

void CollectorVolunteer::setTimeLeft(){
    timeLeft=coolDown;
}

bool CollectorVolunteer::hasOrdersLeft() const{
    return true;
}

void CollectorVolunteer:: acceptOrder(const Order &order){
    setTimeLeft();
    activeOrderId=order.getId();
}

void CollectorVolunteer:: step(){
    if(isBusy()){
        decreaseCoolDown();
        if(getTimeLeft()==0){
            completedOrderId=activeOrderId;
            activeOrderId=NO_ORDER;
        }
    }
}

string CollectorVolunteer::toString() const{
    return "hey";
}

// NEED TO IMPLEMENT TOSTRING()