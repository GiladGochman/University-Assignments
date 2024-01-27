#pragma once
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
    errorMsg = Msg;
}