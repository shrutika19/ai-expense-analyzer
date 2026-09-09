import { lazy, Suspense, type ComponentProps } from "react";

import { ChartSkeleton } from "@/common/states";

const CategoryChart = lazy(() =>
  import("@/dashboard/charts").then((module) => ({ default: module.CategoryChart })),
);
const MonthlyTrendChart = lazy(() =>
  import("@/dashboard/charts").then((module) => ({ default: module.MonthlyTrendChart })),
);
const CategoryBarChart = lazy(() =>
  import("@/dashboard/charts").then((module) => ({ default: module.CategoryBarChart })),
);
const MerchantChart = lazy(() =>
  import("@/dashboard/charts").then((module) => ({ default: module.MerchantChart })),
);
const MomChart = lazy(() =>
  import("@/dashboard/charts").then((module) => ({ default: module.MomChart })),
);

function withChartFallback<T extends object>(
  Component: React.ComponentType<T>,
  height = 360,
) {
  return function LazyChart(props: T) {
    return (
      <Suspense fallback={<ChartSkeleton height={height} />}>
        <Component {...props} />
      </Suspense>
    );
  };
}

export const LazyCategoryChart = withChartFallback(
  CategoryChart,
  360,
) as (props: ComponentProps<typeof CategoryChart>) => React.ReactNode;
export const LazyMonthlyTrendChart = withChartFallback(
  MonthlyTrendChart,
  360,
) as (props: ComponentProps<typeof MonthlyTrendChart>) => React.ReactNode;
export const LazyCategoryBarChart = withChartFallback(CategoryBarChart, 360) as (
  props: ComponentProps<typeof CategoryBarChart>,
) => React.ReactNode;
export const LazyMerchantChart = withChartFallback(MerchantChart, 360) as (
  props: ComponentProps<typeof MerchantChart>,
) => React.ReactNode;
export const LazyMomChart = withChartFallback(MomChart, 360) as (
  props: ComponentProps<typeof MomChart>,
) => React.ReactNode;
