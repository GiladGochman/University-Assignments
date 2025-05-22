import dotenv from 'dotenv';
import app from './expressApp';
import { connectDB } from './config/db'; // או './config/mongo' - תלוי בשם הקובץ אצלך

dotenv.config(); // טוען משתני סביבה מה-.env

const PORT = process.env.PORT || 3001;

const start = async () => {
  await connectDB(); // ממתין להתחברות למסד
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
};

start(); // מפעיל את השרת
