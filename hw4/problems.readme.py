2: Calculation about BN
1) The former is more probable.
   Since P(ST, SI, IN, RE) = P(ST)*P(SI|ST)*P(IN|SI)*P(RE|SI,IN), 
   P(ST=present, SI=high, IN=high, RE=yes) = 0.4*0.6*0.6*0.5 = 0.072
   P(ST=Not present, SI=medium, IN=low, RE=yes) = 0.6*0.2*0.6*0.8 = 0.0576

2) P(ST=present| SI=high, IN=medium, RE=no) = P(ST=present, SI=high, IN=medium, RE=no)/[P(ST=present, SI=high, IN=medium, RE=no) + P(ST=Not present, SI=high, IN=medium, RE=no)]
   = 0.4*0.6*0.3*0.2/(0.4*0.6*0.3*0.2 + 0.6*0.1*0.3*0.2) = 0.8

3) P(ST=present|SI=high, IN=medium) = P(ST=present, SI=high, IN=medium)/[P(ST=present, SI=high, IN=medium) + P(ST=Not present, SI=high, IN=medium)]
   = 0.4*0.6*0.3/(0.4*0.6*0.3 + 0.6*0.1*0.3) = 0.8

3: Calculation about Decision tree
Entropy(original) = -(3/10)log(3/10)-(7/10)log(7/10) = 0.8813

1) Split on Gene A
   Entropy(A) = P(Normal)*Entropy(Normal) + P(Mutation)*Entropy(Mutation) = (4/10)(-log(1/2)) + (6/10)(-1/6log(1/6)-5/6log(5/6)) = 0.7900

2) Split on Gene B
   Entropy(B) = P(Normal)*Entropy(Normal) + P(Mutation)*Entropy(Mutation) = (5/10)(-2/5log(2/5)-3/5log(3/5)) + (5/10)(-1/5log(1/5)-4/5log(4/5)) = 0.8464

3) Split on Age
   Entropy(Age) = P(Old)*Entropy(Old) + P(Young)*Entropy(Young) = (7/10)(-1/7log(1/7)-6/7log(6/7)) + (3/10)(-1/3log(1/3)-2/3log(2/3)) = 0.6897

4) Split on Smoke
   Entropy(Smoke) = P(Yes)*Entropy(Yes) + P(No)*Entropy(No) = (5/10)(-1/5log(1/5)-4/5log(4/5)) + (5/10)(-3/5log(3/5)-2/5log(2/5)) =  0.8207

Therefore, gain(Age) = Entropy(original)-Entropy(Age)=0.1916 is the largest. Therefore, the root of decision tree is "Age".