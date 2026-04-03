package api

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/the-aichronicle/backend/internal/models"
	"github.com/the-aichronicle/backend/internal/repository"
)

type API struct {
	Repo *repository.Repository
}

func (api *API) MountRoutes(r chi.Router) {
	r.Route("/api/v1", func(r chi.Router) {
		r.Get("/articles", api.getArticlesHandler)
		r.Get("/articles/{id}", api.getArticleByIDHandler)
		r.Get("/trends", api.getTrendsHandler)
	})
}

func getLang(r *http.Request) string {
	lang := r.URL.Query().Get("lang")
	if lang == "" {
		return "en"
	}
	return lang
}

func (api *API) getArticlesHandler(w http.ResponseWriter, r *http.Request) {
	lang := getLang(r)

	articles, err := api.Repo.GetArticles(r.Context(), 20, lang)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if articles == nil {
		articles = []models.Article{} 
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(articles)
}

func (api *API) getArticleByIDHandler(w http.ResponseWriter, r *http.Request) {
	lang := getLang(r)
	id := chi.URLParam(r, "id")

	article, err := api.Repo.GetArticleByID(r.Context(), id, lang)
	if err != nil {
		http.Error(w, "Article not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(article)
}

func (api *API) getTrendsHandler(w http.ResponseWriter, r *http.Request) {
	trends, err := api.Repo.GetTrends(r.Context(), 10)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if trends == nil {
		trends = []models.Trend{}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(trends)
}
