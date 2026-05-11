export interface Note {
  _id: any;
  title: string;
  author: {
    name: string;
    email: string;
  };
  content: string;
}
