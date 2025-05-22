import { Request, Response, NextFunction } from 'express';
import fs from 'fs';
import path from 'path';

const logPath = path.join(__dirname, '../log.txt');

export const requestLogger = (req: Request, res: Response, next: NextFunction) => {
  const log = `[${new Date().toISOString()}] ${req.method} ${req.originalUrl} ${JSON.stringify(req.body)}\n`;
  fs.appendFile(logPath, log, err => {
    if (err) console.error('Failed to write log:', err);
  });
  next();
};
