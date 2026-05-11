import { filter } from "ramda";
import { Result, makeFailure, makeOk, bind, either } from "../lib/result";

/* Library code */
const findOrThrow = <T>(pred: (x: T) => boolean, a: T[]): T => {
  for (let i = 0; i < a.length; i++) {
    if (pred(a[i])) return a[i];
  }
  throw "No element found.";
};

export const findResult: <T>(f: (x: T) => boolean, arr: T[]) => Result<T> = <T>(
  predicate: (x: T) => boolean,
  array: T[]
) => {
  const first: T = filter(predicate, array)[0];
  return first ? makeOk(first) : makeFailure("Failed misserably.");
};

/* Client code */
const returnSquaredIfFoundEven_v1 = (a: number[]): number => {
  try {
    const x = findOrThrow((x) => x % 2 === 0, a);
    return x * x;
  } catch (e) {
    return -1;
  }
};

export const returnSquaredIfFoundEven_v2: (a: number[]) => Result<number> = (
  arr
) => {
  return bind(
    findResult((x: number) => x % 2 == 0, arr),
    (y: number) => makeOk(y * y)
  );
};

export const returnSquaredIfFoundEven_v3 = (arr: number[]) => {
  const first: Result<number> = findResult((x: number) => x % 2 == 0, arr);
  return either(
    first,
    (x: number) => x * x,
    (s: string) => -1
  );
};
