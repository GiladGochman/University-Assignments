import * as R from "ramda";

const stringToArray = R.split("");

/* Question 1 */
export const countVowels: (s: string) => number = (str) => {
  const vowels: string[] = stringToArray("aeiouAEIOU");
  return R.filter((c) => R.includes(c, vowels), stringToArray(str)).length;
};

/* Question 2 */
export const isPaired: (s: string) => boolean = (str: string) => {
  const countParentheses: (
    numRound: number,
    numSquare: number,
    numSquiggly: number,
    s: string
  ) => boolean = (round, square, squig, input) => {
    const parentheses: string[] = stringToArray("(){}[]");

    if (round < 0 || square < 0 || squig < 0) return false; //unopened parenthesis
    if (!input && round == 0 && square == 0 && squig == 0) return true; // finnished string condition met
    const firstChar: string = input.charAt(0);
    const nextInput: string = input.substring(1);
    switch (firstChar) {
      case "(":
        return countParentheses(round + 1, square, squig, nextInput);
      case ")":
        return countParentheses(round - 1, square, squig, nextInput);
      case "[":
        return countParentheses(round, square + 1, squig, nextInput);
      case "]":
        return countParentheses(round, square - 1, squig, nextInput);
      case "{":
        return countParentheses(round, square, squig + 1, nextInput);
      case "}":
        return countParentheses(round, square, squig - 1, nextInput);
      case "":
        return false; //finished string, unclosed parenthesis
      default:
        return countParentheses(round, square, squig, nextInput);
    }
  };
  return countParentheses(0, 0, 0, str);
};
/* Question 3 */
export type WordTree = {
  root: string;
  children: WordTree[];
};

export const treeToSentence: (t: WordTree) => string = (tree) => {
  return (
    tree.root +
    //Makes a function that recieves an array of Wordtrees
    // and first creates an array that containes a "tree to sentence" of each child
    // and then joins all the strings in the array:
    R.pipe(
      R.map((child: WordTree) => " " + treeToSentence(child)),
      R.join("")
    )(tree.children)
  );
};
