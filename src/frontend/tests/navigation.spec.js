import { test, expect } from '@playwright/test';

test('switch views without rendering a previous response as new analysis data', async ({ page }) => {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  // Make the request boundary visible and exercise cancellation on rapid switches.
  await page.route('**/api/analysis/**', async route => {
    await new Promise(resolve => setTimeout(resolve, 200));
    await route.continue();
  });
  await page.goto('/');
  await expect(page.getByRole('columnheader', { name: 'age', exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Distributions', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Descriptive statistics (unweighted)' })).toBeVisible();
  await expect(page.locator('.bar-row')).toHaveCount(20);
  await page.getByRole('checkbox', { name: 'Weight by fnlwgt' }).check();
  await expect(page.locator('.bar-row')).toHaveCount(20);
  await page.getByRole('button', { name: 'Correlations', exact: true }).click();
  await expect(page.getByRole('table')).toContainText('Pearson correlation');
  await page.getByRole('combobox', { name: 'Method' }).selectOption('cramers_v');
  await expect(page.getByRole('table')).toContainText('Cramér’s V');
  await page.getByRole('button', { name: 'Data', exact: true }).click();
  await expect(page.getByRole('columnheader', { name: 'age', exact: true })).toBeVisible();
  for (const name of ['Distributions', 'Correlations', 'Data', 'Correlations', 'Distributions']) {
    await page.getByRole('button', { name, exact: true }).click();
  }
  await expect(page.locator('.bar-row')).toHaveCount(20);
  await expect(page.getByRole('alert')).toHaveCount(0);
  expect(errors).toEqual([]);
});
