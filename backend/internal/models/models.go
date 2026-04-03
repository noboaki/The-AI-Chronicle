package models

import "time"

type Article struct {
	ID              string     `json:"id"`
	TrendID         *string    `json:"trend_id,omitempty"`
	Title           string     `json:"title"`
	Subtitle        *string    `json:"subtitle,omitempty"`
	Content         *string    `json:"content,omitempty"`
	Summary         *string    `json:"summary,omitempty"`
	Category        *string    `json:"category,omitempty"`
	AIModel         *string    `json:"ai_model,omitempty"`
	ConfidenceScore *float64   `json:"confidence_score,omitempty"`
	Status          string     `json:"status"`
	PublishedAt     *time.Time `json:"published_at,omitempty"`
	CreatedAt       time.Time  `json:"created_at"`
}

type Trend struct {
	ID        string    `json:"id"`
	Title     string    `json:"title"`
	RankScore float64   `json:"rank_score"`
	Status    string    `json:"status"`
	CreatedAt time.Time `json:"created_at"`
}
