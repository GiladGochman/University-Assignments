#pragma once
#include <vector>
#include <string>

class BaseAction
{
    // ... Other members

public:
    enum class ActionStatus
    {
        COMPLETED,
        ERROR
    };

    enum class CustomerType
    {
        Soldier,
        Civilian
    };
    virtual ~BaseAction() = default;

    // ... Other members
};
