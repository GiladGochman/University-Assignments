#pragma once
#include <string>
#include <vector>
using namespace std;

#include "Order.h"
#include "Customer.h"

class BaseAction;
class Volunteer;

// Warehouse responsible for Volunteers, Customers and Actions.

class WareHouse
{

public:
    WareHouse(const string &configFilePath);
    WareHouse(const WareHouse &other);
    WareHouse &operator=(const WareHouse &other);
    WareHouse(WareHouse &&other);
    WareHouse &operator=(WareHouse &&other);
    ~WareHouse();
    void start();
    const vector<BaseAction *> &getActionsLog() const;
    const vector<Volunteer *> &getVolunteerVector() const;
    const vector<Order *> &getPendingOrdersVector() const;
    const vector<Order *> &getInProgressVector() const;
    const vector<Order *> &getCompletedOrdersVector() const;
    const vector<Customer *> &getCustomersVector() const;
    void addOrder(Order *order);
    void addCustomer(Customer *customer);
    void addAction(BaseAction *action);
    void printActionsLogs();
    Customer &getCustomer(int customerId) const;
    Volunteer &getVolunteer(int volunteerId) const;
    Order &getOrder(int orderId) const;
    void close();
    void open();
    bool checkIfCustomerExsists(int id);
    bool checkIfOrderExsists(int id);
    int getOrderCounter();
    int getCustomerCounter();
    void setVolunteerCounter(int numW);
    void setCustomerCounter(int num);
    void assignOrder(Order *order);
    void moveFromVolunteerOrder(vector<Order *>::const_iterator it);
    vector<Volunteer*>::const_iterator &fireVolunteer(vector<Volunteer *>::const_iterator it);


private:
    bool isOpen;
    vector<BaseAction *> actionsLog;
    vector<Volunteer *> volunteers;
    vector<Order *> pendingOrders;
    vector<Order *> vol;
    vector<Order *> completedOrders;
    vector<Customer *> customers;
    int customerCounter;                                  // For assigning unique customer IDs
    int volunteerCounter;                                 // For assigning unique volunteer IDs
    int orderCounter;                                     // for assigning unique order IDs
    std::string trimLeadingWhitespace(const string &str); // For trim leading white spaces in strings
    void parseFile(const string &filePath);               // Function to parse the file.
};
