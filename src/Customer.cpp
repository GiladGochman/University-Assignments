#include <string>
#include <vector>
#include "../include/Customer.h"
#include "../include/Order.h"
using std::string;
using std::vector;


Customer::Customer(int id, const string &name, int locationDistance, int maxOrders) : id(id), name(name), locationDistance(locationDistance), maxOrders(maxOrders){
    ordersId=vector<int>();
}

const string &Customer::getName() const {
    return name;
}

int Customer:: getId() const{
    return id;
}

int Customer:: getCustomerDistance() const {
    return locationDistance;
}

int Customer:: getMaxOrders() const{
    return maxOrders;
}

int Customer:: getNumOrders() const{
    return ordersId.size();
}

bool Customer:: canMakeOrder() const{
  return getNumOrders()<=maxOrders;
}

const vector<int> &Customer::getOrders() const {
     return ordersId;
}

int Customer::addOrder(int orderId){
    if(canMakeOrder){
        ordersId.push_back(orderId);
        return orderId;
    }
    return -1;
}

SoldierCustomer :: SoldierCustomer(int id, string name, int locationDistance, int maxOrders) : Costumer(id, name, locationDistance, maxOrders){};

SoldierCustomer *SoldierCustomer::clone(){
   return new SoldierCustomer(*this)
}

CivilianCustomer :: CivilianCustomer(int id, string name, int locationDistance, int maxOrders) : Costumer(id, name, locationDistance, maxOrders){};

CivilianCustomer *CivilianCustomer::clone(){
   return new CivilianCustomer(*this)
}