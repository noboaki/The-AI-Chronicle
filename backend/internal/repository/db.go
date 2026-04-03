package repository

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/the-aichronicle/backend/internal/models"
)

type Repository struct {
	Pool *pgxpool.Pool
}

func NewRepository(ctx context.Context, dbURL string) (*Repository, error) {
	pool, err := pgxpool.New(ctx, dbURL)
	if err != nil {
		return nil, fmt.Errorf("unable to create connection pool: %w", err)
	}
	return &Repository{Pool: pool}, nil
}

// GetArticles fetches published articles, falling back to English if translation is missing
func (r *Repository) GetArticles(ctx context.Context, limit int, lang string) ([]models.Article, error) {
	// Base query defaults to original if no language translation matches
	query := `
		SELECT 
			a.id, 
			a.trend_id::text, 
			COALESCE(t.title, a.title) as title, 
			COALESCE(t.subtitle, a.subtitle) as subtitle, 
			COALESCE(t.content, a.content) as content, 
			COALESCE(t.summary, a.summary) as summary, 
			a.category, a.ai_model, a.confidence_score, a.status, a.published_at, a.created_at
		FROM articles a
		LEFT JOIN article_translations t 
		  ON t.article_id = a.id AND t.language_code = $1
		WHERE a.status = 'published' 
		ORDER BY a.published_at DESC 
		LIMIT $2`
		
	rows, err := r.Pool.Query(ctx, query, lang, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var articles []models.Article
	for rows.Next() {
		var a models.Article
		err := rows.Scan(&a.ID, &a.TrendID, &a.Title, &a.Subtitle, &a.Content, &a.Summary, &a.Category, &a.AIModel, &a.ConfidenceScore, &a.Status, &a.PublishedAt, &a.CreatedAt)
		if err != nil {
			return nil, err
		}
		articles = append(articles, a)
	}
	return articles, nil
}

func (r *Repository) GetArticleByID(ctx context.Context, id string, lang string) (*models.Article, error) {
	query := `
		SELECT 
			a.id, 
			a.trend_id::text, 
			COALESCE(t.title, a.title), 
			COALESCE(t.subtitle, a.subtitle), 
			COALESCE(t.content, a.content), 
			COALESCE(t.summary, a.summary), 
			a.category, a.ai_model, a.confidence_score, a.status, a.published_at, a.created_at
		FROM articles a
		LEFT JOIN article_translations t 
		  ON t.article_id = a.id AND t.language_code = $1
		WHERE a.id = $2`
		
	var a models.Article
	err := r.Pool.QueryRow(ctx, query, lang, id).Scan(&a.ID, &a.TrendID, &a.Title, &a.Subtitle, &a.Content, &a.Summary, &a.Category, &a.AIModel, &a.ConfidenceScore, &a.Status, &a.PublishedAt, &a.CreatedAt)
	if err != nil {
		return nil, err
	}
	return &a, nil
}

func (r *Repository) GetTrends(ctx context.Context, limit int) ([]models.Trend, error) {
	query := `SELECT id, title, rank_score, status, created_at FROM trends WHERE status = 'detected' ORDER BY rank_score DESC LIMIT $1`
	rows, err := r.Pool.Query(ctx, query, limit)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var trends []models.Trend
	for rows.Next() {
		var t models.Trend
		err := rows.Scan(&t.ID, &t.Title, &t.RankScore, &t.Status, &t.CreatedAt)
		if err != nil {
			return nil, err
		}
		trends = append(trends, t)
	}
	return trends, nil
}
