import { Request, Response, NextFunction } from 'express';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { User } from '../models/User';
import { JWT_SECRET } from '../config/env';

export const login = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { username, password } = req.body;
    const user = await User.findOne({ username });
    if (!user || !(await bcrypt.compare(password, user.passwordHash)))
      return res.status(401).json({ error: 'invalid credentials' });

    const token = jwt.sign({ id: user._id }, JWT_SECRET!, { expiresIn: '1h' });
    res.json({ token, username: user.username, name: user.name });
  } catch (err) { next(err); }
};