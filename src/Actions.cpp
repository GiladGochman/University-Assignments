
#pragma once
#include <vector>
#include <string>
#include "../include/Action.h"
#include "../include/WareHouse.h"
#include "../include/Order.h"
#include <iostream>
#include <cstdio>

AddOrder::AddOrder(int id) : BaseAction(), customerId(id) {}

void AddOrder::act(WareHouse &wareHouse)
{
    if (wareHouse.checkIfCustomerExsists(customerId))
    {
        int isAdded = wareHouse.getCustomer(customerId).addOrder(wareHouse.getOrderCounter()); // Trys to add an order (expected = orderID, if customer can't order will return -1)
        if (isAdded == -1)
        {
            error("Customer can't order!");
            cout << "ERROR: " << getErrorMsg() << endl;
        }
        else
        { // Customer could order
            int orderDistance = wareHouse.getCustomer(customerId).getCustomerDistance();
            Order *newOrder = new Order(isAdded, customerId, orderDistance);
            wareHouse.addOrder(newOrder);
            complete();
        }
    }
    else
    {
        error("Customer doesn't exist!");
        cout << "ERROR: " << getErrorMsg() << endl;
    }
}

AddOrder *AddOrder::clone() const
{
    return new AddOrder(*this);
}
string AddOrder::toString() const
{
    if (ActionStatus::COMPLETED == getStatus())
    {
        return "order " + to_string(customerId) + "COMPLETED";
    }
    return "order " + to_string(customerId) + "ERROR";
}

AddCustomer::AddCustomer(string customerName, string customerType, int distance, int maxOrders) : BaseAction(), customerName(customerName), customerType(CustomerType(convertCustomerType(customerType))), distance(distance), maxOrders(maxOrders)
{
}
void AddCustomer::act(WareHouse &wareHouse)
{
    int id = wareHouse.getCustomerVector().size();
    if (customerType == CustomerType::Soldier)
        Customer *newCustomer = new SoldierCustomer(wareHouse.getCustomerCounter(), customerName, distance, maxOrders);
    if (customerType == CustomerType::Civilian)
        Customer *newCustomer = new CivilianCustomer(wareHouse.getCustomerCounter(), customerName, distance, maxOrders);
}
int AddCustomer::convertCustomerType(string customerType)
{
    if (customerType == "soldier")
    {
        return 0;
    }
    if (customerType == "civilian")
    {
        return 1;
    }
}

AddCustomer *AddCustomer::clone() const
{
    return new AddCustomer(*this);
}
string AddCustomer::toString() const
{
    string res = "customer " + customerName;
    if (customerType == CustomerType::Soldier)
    {
        res += " soldier ";
    }
    else if (customerType == CustomerType::Civilian)
    {
        res += " civilian ";
    }
    res += to_string(distance) + " " + to_string(maxOrders) + " ";

    if (ActionStatus::COMPLETED == getStatus())
    {
        return res + "COMPLETED";
    }
    return res + "ERROR";
}