import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { JWT_SECRET } from '../config/env';
import { User } from '../models/User';

export interface AuthReq extends Request {
  user?: any;
}

export const auth = async (req: AuthReq, res: Response, next: NextFunction) => {
  const header = req.get('Authorization');
  if (!header?.startsWith('Bearer ')) return res.status(401).json({ error: 'token missing' });
  const token = header.replace('Bearer ', '');
  try {
    const data = jwt.verify(token, JWT_SECRET!) as { id: string };
    const user = await User.findById(data.id);
    if (!user) return res.status(401).json({ error: 'user not found' });
    req.user = user;
    next();
  } catch {
    res.status(401).json({ error: 'token invalid' });
  }
};