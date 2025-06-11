import { Request, Response, NextFunction } from 'express';
import bcrypt from 'bcrypt';
import { User } from '../models/User';

export const createUser = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { name, email, username, password } = req.body;
    if (!password) {
      return res
        .status(400)
        .json({ error: 'password is required' });
    }
    const hash = await bcrypt.hash(password, 10);
    const user = new User({ name, email, username, passwordHash: hash });
    const saved = await user.save();
    res.status(201).json({
      id: saved._id, name: saved.name, email: saved.email, username: saved.username
    });
  } catch (err) { next(err); }
};