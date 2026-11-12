// Notebook observations and user-approved additions about the full dataset.
export const distributionNotes = {
  age: 'The age distribution is right-skewed, with many records representing people younger than 45.',
  education_num: 'The education distribution is concentrated at education levels 9 and 10.',
  education: 'The education distribution is concentrated at education levels 9 and 10.',
  capital_gain: 'Capital gains are zero in 91.73% of records, while capital losses are zero in 95.33%. These values alone do not establish whether respondents invest.',
  capital_loss: 'Capital gains are zero in 91.73% of records, while capital losses are zero in 95.33%. These values alone do not establish whether respondents invest.',
  hours_per_week: 'Around 48% of the people represented work approximately 40 hours per week. A value of 99 hours per week appears to be an outlier.',
  sex: 'Male is the predominant category.',
  race: 'White is the predominant category.',
  workclass: 'Private is the predominant category.',
  native_country: 'United States accounts for 91.35% of records, strongly dominating the country distribution.',
  marital_status: 'Married-civ-spouse is the largest category (45.83%), followed by Never-married (32.98%).',
  occupation: 'Prof-specialty (13.41%), Craft-repair (13.27%) and Exec-managerial (13.22%) have similar shares.',
  relationship: 'Husband is the largest category (40.38%), followed by Not-in-family (25.75%).',
  income: '76.06% of records belong to the <=50K class, compared with 23.94% in the >50K class.',
};

export const correlationNotes = {
  pearson: 'The Pearson matrix indicates a weak linear correlation between capital_gain and education_num.',
  cramers_v: 'Moderate associations are observed between race and native_country, relationship and marital_status, and occupation and workclass.',
};
