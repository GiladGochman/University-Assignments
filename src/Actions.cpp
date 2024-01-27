
#pragma once
#include <vector>
#include <string>
#include "../include/Action.h"
#include "../include/WareHouse.h"
#include "../include/Order.h"

AddOrder::AddOrder(int id) : BaseAction(), customerId(id) {}

void AddOrder::act(WareHouse &wareHouse)
{
    if (wareHouse.checkIfCustomerExsists(customerId))
    {
        int isAdded = wareHouse.getCustomer(customerId).addOrder(wareHouse.getOrderCounter()); // Trys to add an order (expected = orderID, if customer can't order will return -1)
        if (isAdded == -1)
        {
            error("Customer can't order!");
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
    }
}

AddOrder *clone() const
{
}
string toString() const override;