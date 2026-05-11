import { ClassExp, ProcExp, Exp, Program, makeVarDecl, makeVarRef, makeIfExp, makeAppExp, makePrimOp, makeLitExp, makeProcExp, isClassExp, isDefineExp, makeDefineExp, makeProgram, isBoolExp, isNumExp, isStrExp, isLitExp, isVarRef, isProcExp, isIfExp, isAppExp, isPrimOp, isLetExp, isProgram, CExp, makeLetExp, makeBinding, makeClassExp, isCExp, isExp, isAtomicExp, IfExp, makeBoolExp } from "./L3-ast";
import { Result, bind, makeFailure, makeOk, mapResult } from "../shared/result";
import { map, reduce, reduceRight } from "ramda";
import { makeSymbolSExp } from "./L3-value";
import { first, second, rest, allT, isEmpty, isNonEmptyList, List } from "../shared/list";
import {  } from "../shared/list";

/*
Purpose: Transform ClassExp to ProcExp
Signature: class2proc(classExp)
Type: ClassExp => ProcExp
*/
export const class2proc = (exp: ClassExp): ProcExp => {
    const fields = exp.fields;
    const methods = exp.methods;

    const msgVar = makeVarDecl('msg');

    const methodCases = map((method) => {
        const methodName = method.var.var;
        const methodBody = method.val;

        return makeIfExp(
            makeAppExp(makePrimOp('eq?'), [makeVarRef('msg'), makeLitExp(makeSymbolSExp(methodName))]),
            makeAppExp(methodBody, []),
            makeBoolExp(false)
        );
    }, methods);

    const nestedIf = reduce(
        (acc, methodCase) => makeIfExp(methodCase.test, methodCase.then, acc),
        makeBoolExp(false) as CExp,
        methodCases.reverse()
    );

    return makeProcExp(fields, [makeProcExp([msgVar], [nestedIf])]);
};
  
/*
Purpose: Transform all class forms in the given AST to procs
Signature: lexTransform(AST)
Type: [Exp | Program] => Result<Exp | Program>
*/
export const lexTransform = (exp: Exp | Program): Result<Exp | Program> => { 
    const transformExp = (exp: Exp): Exp =>
        isCExp(exp) ? transformCExp(exp) :
        isDefineExp(exp) ? makeDefineExp(exp.var, transformCExp(exp.val)) :
        exp;
    
    const transformCExp = (cexp: CExp): CExp => 
            isAtomicExp(cexp) ? cexp :
            isLitExp(cexp) ? cexp :
            isProcExp(cexp) ? makeProcExp(cexp.args, map(transformCExp, cexp.body)) :
            isIfExp(cexp) ? makeIfExp(transformCExp(cexp.test), transformCExp(cexp.then), transformCExp(cexp.alt)) :
            isAppExp(cexp) ? makeAppExp(transformCExp(cexp.rator), map(transformCExp, cexp.rands)) :
            isLetExp(cexp) ? makeLetExp(map(binding => makeBinding(binding.var.var, transformCExp(binding.val)), cexp.bindings), map(transformCExp, cexp.body)) :
            isClassExp(cexp) ? class2proc(makeClassExp(cexp.fields, map(method => makeBinding(method.var.var, transformCExp(method.val)), cexp.methods))) :
            cexp;

    return isExp(exp) ? makeOk(transformExp(exp)) :
    isProgram(exp) ? makeOk(makeProgram(map(transformExp, exp.exps))) :
    exp;
};