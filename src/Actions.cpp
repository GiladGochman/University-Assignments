

#include <vector>
#include <string>
#include "../include/Action.h"
#include "../include/WareHouse.h"
#include "../include/Order.h"
#include "../include/Volunteer.h"
#include <algorithm>
#include <iostream>
#include <cstdio>
#include <vector>
#include <string>
#include "../include/Action.h"

BaseAction::BaseAction() : status(ActionStatus::ERROR), errorMsg("") {}

ActionStatus BaseAction::getStatus() const
{
    return status;
}

void BaseAction::complete()
{
    status = ActionStatus::COMPLETED;
}

void BaseAction::error(string Msg)
{
    status = ActionStatus::ERROR;
    errorMsg = Msg;
}

string BaseAction::getErrorMsg() const
{
    return errorMsg;
}

//////////////AddOrder///////////////
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
//////////////////////////////////////////AddCustomer///////////////////////////////////
AddCustomer::AddCustomer(string customerName, string customerType, int distance, int maxOrders) : BaseAction(), customerName(customerName), customerType(CustomerType(convertCustomerType(customerType))), distance(distance), maxOrders(maxOrders)
{
}
void AddCustomer::act(WareHouse &wareHouse)
{
    int id = wareHouse.getCustomersVector().size();
    if (customerType == CustomerType::Soldier)
        Customer *newCustomer = new SoldierCustomer(wareHouse.getCustomerCounter(), customerName, distance, maxOrders);
    if (customerType == CustomerType::Civilian)
        Customer *newCustomer = new CivilianCustomer(wareHouse.getCustomerCounter(), customerName, distance, maxOrders);
    complete();
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
///////////////////////////////PrintOrderStatus////////////////////////////////////
PrintOrderStatus::PrintOrderStatus(int id) : BaseAction(), orderId(id) {}

void PrintOrderStatus::act(WareHouse &warehouse)
{
    if (!warehouse.checkIfOrderExsists(orderId))
    {
        error("Order doesn't exist.");
        cout << "Error: " << getErrorMsg() << endl;
        return;
    }
    Order order = warehouse.getOrder(orderId);
    cout << "OrderId: " + to_string(orderId) << endl;
    cout << "OrderStatus: " + to_String(order.getStatus()) << endl;
    cout << "CustomerID: " + to_string(order.getCustomerId()) << endl;
    cout << "Collector: " + volunteerIdToString(order.getCollectorId()) << endl;
    cout << "Driver: " + volunteerIdToString(order.getDriverId()) << endl;
    complete();
}

PrintOrderStatus *PrintOrderStatus::clone() const
{
    return new PrintOrderStatus(*this);
}

string PrintOrderStatus::toString() const
{
    return "orderStatus " + to_string(orderId);
}

std::string BaseAction::to_String(OrderStatus status)
{
    switch (status)
    {
    case OrderStatus::PENDING:
        return "Pending";
    case OrderStatus::COLLECTING:
        return "Collecting";
    case OrderStatus::DELIVERING:
        return "Delivering";
    case OrderStatus::COMPLETED:
        return "Completed";
    default:
        return "Unknown"; // Handle unknown status, if necessary
    }
}
std::string BaseAction::volunteerIdToString(int volId)
{
    if (volId == -1)
        return "None";
    return to_string(volId);
}
////////////////////////////// printCustomerStatus////////////////////////////

PrintCustomerStatus::PrintCustomerStatus(int customerId) : BaseAction(), customerId(customerId) {}

void PrintCustomerStatus::act(WareHouse &wareHouse)
{
    if (!wareHouse.checkIfCustomerExsists(customerId))
    {
        error("Customer doesn't exsist.");
        cout << "ERROR: " + getErrorMsg() << endl;
        return;
    }
    cout << "CustomerID: " + to_string(customerId) << endl;
    for (int orderId : wareHouse.getCustomer(customerId).getOrdersId())
    {
        cout << "OrderStatus: " << to_String(wareHouse.getOrder(orderId).getStatus()) << endl;
    }
    cout << "numOrdersLeft: " + to_string(wareHouse.getCustomer(customerId).getNumOrders()) << endl;
    complete();
}

PrintCustomerStatus *PrintCustomerStatus::clone() const
{
    return new PrintCustomerStatus(*this);
}

string PrintCustomerStatus::toString() const
{
    if (getStatus() == ActionStatus::ERROR)
    {
        return "customerStatus " + to_string(customerId) + " ERROR";
    }
    return "customerStatus " + to_string(customerId) + " COMPLETE";
}
////////////////////////////////////////PrintVolunteerStatus/////////////////////////////////
PrintVolunteerStatus::PrintVolunteerStatus(int id) : BaseAction(), VolunteerId(id) {}

void PrintVolunteerStatus::act(WareHouse &wareHouse)
{
}

PrintVolunteerStatus *PrintVolunteerStatus::clone() const
{
    return new PrintVolunteerStatus(*this);
}

string PrintVolunteerStatus::toString() const
{
    return "volunteerStatus " + to_string(VolunteerId);
}

////////////////////////SimulateStep/////////////////////////

SimulateStep::SimulateStep(int numOfSteps) : BaseAction(), numOfSteps(numOfSteps) {}
void SimulateStep::act(WareHouse &wareHouse)
{
    for (int i = 0; i < numOfSteps; i++)
    {
        
        // 1. iterate pending orders vector and assign orders to free volunteers
        assignJobs(wareHouse);
        
        // 2. iterate busy volunteers: decrease distance of drivers and decrease collectors cooldown
        promoteOrders(wareHouse);
    
        // 3. iterate volunteers and check who reached their destinations / finnished collecting and changes the order status and move to pending/completed vector.
        freeUpVolunteers(wareHouse);
    
        // 4. iterate volunteers and remove limited ones from the vector
        fireVolunteers(wareHouse);
        
        // 5. enjoy!
    }
    complete();
}

SimulateStep *SimulateStep::clone() const
{
    return new SimulateStep(*this);
}

string SimulateStep::toString() const
{
    return "step " + to_string(numOfSteps);
}

void SimulateStep::assignJobs(WareHouse &wareHouse)
{
    vector<Order *>::const_iterator it=wareHouse.getPendingOrdersVector().begin();
    while (it != wareHouse.getPendingOrdersVector().end()){
        Order *order=*it;
        bool found= false;
        if(order->getStatus()==OrderStatus::PENDING){
            
            auto volunteerIt=wareHouse.getVolunteerVector().begin();
            while(!found && volunteerIt !=wareHouse.getVolunteerVector().end()){
                auto volunteer=*volunteerIt;

                if(volunteer->type()=="Collector" || volunteer->type()=="LimitedCollector"){
                    if(volunteer->canTakeOrder(*order)){
                        
                        volunteer->acceptOrder(*order);
                        found=true;
                        order->setStatus(OrderStatus::COLLECTING);
                        wareHouse.assignOrder(it);
                    }
                }
                ++volunteerIt;
            }
        }
        else if(order->getStatus()==OrderStatus::COLLECTING){
            auto volunteerIt=wareHouse.getVolunteerVector().begin();
           
            while(!found && volunteerIt !=wareHouse.getVolunteerVector().end()){
                auto volunteer=*volunteerIt;
                if(volunteer->type()=="Driver" || volunteer->type()=="LimitedDriver`"){
                    if(volunteer->canTakeOrder(*order)){
                        volunteer->acceptOrder(*order);
                        found=true;
                        order->setStatus(OrderStatus::DELIVERING);
                        wareHouse.assignOrder(it);
                    }
                }
                ++volunteerIt;
            }
        }
        if(!found) ++it;
        
        
    }
    
  
}
void SimulateStep::promoteOrders(WareHouse &wareHouse)
{
    for (auto volunteer : wareHouse.getVolunteerVector())
    {

        if (volunteer->type() == "Collector")
        {
            CollectorVolunteer *castedVol = dynamic_cast<CollectorVolunteer *>(volunteer);
            
                castedVol->step();
            
        }

         if (volunteer->type() == "LimitedCollector")
        {
            LimitedCollectorVolunteer *castedVol = dynamic_cast<LimitedCollectorVolunteer *>(volunteer);
           
                castedVol->step();
            
        }

         if (volunteer->type() == "Driver")
        {
            DriverVolunteer *castedVol = dynamic_cast<DriverVolunteer *>(volunteer);
            
                castedVol->step();
            
        }
         if (volunteer->type() == "LimitedDriver")
        {
            LimitedDriverVolunteer *castedVol = dynamic_cast<LimitedDriverVolunteer *>(volunteer);
           
                castedVol->step();
            
        }
    }
}
void SimulateStep::freeUpVolunteers(WareHouse &wareHouse)
{
    for(auto volu : wareHouse.getVolunteerVector()){
        if(volu->hasJustFinishedJob()){
            

            int finishedId=volu->getCompletedOrderId();

            auto it= find_if(wareHouse.getInProgressVector().begin(), wareHouse.getInProgressVector().end(),[finishedId](const Order *order){
                return order!=nullptr && order->getId()==finishedId;
            } );
            
            wareHouse.moveFromVolunteerOrder(it);
        }
    }
    
}
void SimulateStep::fireVolunteers(WareHouse &wareHouse)
{
    vector<Volunteer *>::const_iterator it = wareHouse.getVolunteerVector().begin();
    while (it != wareHouse.getVolunteerVector().end())
    {
        const std::type_info &type = typeid(*it);
        if (type.name() == "LimitedDriverVolunteer")
        {
            auto castedVol = dynamic_cast<LimitedDriverVolunteer *>(*it);
            if (!castedVol->isBusy() && !castedVol->hasOrdersLeft())
            {
                it = wareHouse.fireVolunteer(it);
                delete castedVol;
            }
        }

        if (type.name() == "LimitedCollectorVolunteer")
        {
            auto castedVol = dynamic_cast<LimitedCollectorVolunteer *>(*it);
            if (!castedVol->isBusy() && !castedVol->hasOrdersLeft())
            {
                it = wareHouse.fireVolunteer(it);
                delete castedVol;
            }
        }
        ++it;
    }
}