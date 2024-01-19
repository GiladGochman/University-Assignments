#include "../include/Volunteer.h"
#include "../include/Order.h"
#include <vector>
#include <string>

Volunteer::Volunteer(int id, const string &name): id(id), name(name), activeOrderId(NO_ORDER), completedOrderId(NO_ORDER) {}

int Volunteer::getId() const{
    return id;
}

const string &Volunteer::getName() const{
    return name;
}

int Volunteer::getActiveOrderId() const{
    return activeOrderId;
}

int Volunteer::getCompletedOrderId() const{
    return completedOrderId;
}

bool Volunteer::isBusy() const{
    return activeOrderId!=NO_ORDER;
}

