// Auth
export interface AuthTokens { access_token:string; refresh_token:string; token_type:string; expires_in:number }
export interface LoginRequest { email:string; password:string }
export interface RegisterRequest { name:string; email:string; password:string; role:string }

// User
export interface User { id:string; name:string; email:string; role:string; is_active:boolean; is_verified:boolean; created_at:string; updated_at:string }

// Subscription
export interface SubscriptionPlan { id:string; name:'Basic'|'Pro'|'Premium'; type:string; price:number; features:Record<string,boolean|number>; is_active:boolean }
export interface Subscription { id:string; user_id:string; plan_id:string; status:string; start_date:string; end_date?:string; plan?:SubscriptionPlan; created_at:string }

// Trends
export type TrendStatus = 'emerging'|'rising'|'peak'|'declining'|'stable'
export interface Trend { id:string; name:string; category:string; trend_score:number; growth_rate:number; region:string; status:TrendStatus; date:string; color_hex?:string; top_hashtags?:string[]; source_breakdown:Record<string,{normalized_score:number}>; created_at:string; updated_at:string }
export interface TrendListResponse { trends:Trend[]; total:number; page:number; page_size:number; has_next:boolean }
export interface TrendFilter { category?:string; region?:string; status?:TrendStatus; min_score?:number; search?:string; sort_by?:'trend_score'|'growth_rate'|'date'|'name'; sort_order?:'asc'|'desc'; page?:number; page_size?:number }

// Predictions
export interface TrendPrediction { id:string; trend_id:string; predicted_value:number; prediction_date:string; confidence:number; model_used:string; horizon_days:number; lower_bound?:number; upper_bound?:number; season?:string; factors:Record<string,unknown>; trend?:Trend; created_at:string }
export interface SeasonForecast { season:string; trend_name:string; confidence:number; description:string; predicted_score:number; key_factors:string[] }

// Recommendations
export type RecommendationAction = 'stock_now'|'avoid'|'monitor'|'reduce_inventory'|'feature_prominently'
export type Priority = 'high'|'medium'|'low'
export interface Recommendation { id:string; user_id:string; trend_id:string; action:RecommendationAction; description:string; priority:Priority; confidence_score:number; is_read:boolean; ai_reasoning?:string; trend?:Trend; created_at:string }

// Alerts
export type AlertType = 'trend_spike'|'trend_decline'|'new_trend'|'recommendation'
export type AlertChannel = 'email'|'sms'|'push'|'in_app'
export interface Alert { id:string; user_id:string; trend_id?:string; alert_type:AlertType; threshold?:number; triggered:boolean; triggered_at?:string; triggered_value?:number; channels:AlertChannel[]; message?:string; is_active:boolean; created_at:string }
export interface AlertCreateRequest { trend_id?:string; alert_type:AlertType; threshold?:number; channels:AlertChannel[] }

// Reports
export type ReportType = 'weekly_trends'|'color_palette'|'season_forecast'|'recommendations'|'custom'
export type ReportStatus = 'pending'|'generating'|'ready'|'failed'
export interface Report { id:string; user_id:string; title:string; report_type:ReportType; file_url?:string; status:ReportStatus; filters:Record<string,unknown>; created_at:string }
export interface ReportCreateRequest { title:string; report_type:ReportType; filters?:Record<string,unknown> }

// Dashboard
export interface DashboardSummary { total_trends_tracked:number; data_points_today:number; prediction_accuracy:number; active_brands:number; top_trends:Trend[]; agent_status:Record<string,string>; last_updated:string }

// Colors
export interface ColorTrend { color_name:string; hex_code:string; percentage:number; growth_rate:number; trend_status:TrendStatus; category_breakdown:Record<string,number>; top_brands:string[] }
export interface ColorPalette { season:string; colors:ColorTrend[]; generated_at:string }

// Advisor
export interface AdvisorMessage { role:'user'|'ai'; text:string; timestamp?:string }
export interface AdvisorResponse { response:string; sources_used:string[]; related_trends:string[]; suggested_actions:string[] }

// API Error
export interface ApiError { detail:string|{msg:string;type:string}[] }
