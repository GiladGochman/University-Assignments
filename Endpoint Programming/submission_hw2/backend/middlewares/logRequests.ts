import { Request, Response, NextFunction } from "express";

export const logRequests = (
  req: Request,
  _res: Response,
  next: NextFunction
) => {
  const now = new Date().toISOString();
  console.log(`[${now}] ${req.method} ${req.path}`);
  if (Object.keys(req.body).length) {
    console.log("Body:", req.body);
  }
  next();
};
