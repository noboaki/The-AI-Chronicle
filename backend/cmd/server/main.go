package main

import (
	"context"
	"log"
	"net/http"
	"os"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/the-aichronicle/backend/internal/api"
	"github.com/the-aichronicle/backend/internal/repository"
)

func main() {
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		dbURL = "postgres://chronicle:password@localhost:5432/chronicle_db"
	}

	repo, err := repository.NewRepository(context.Background(), dbURL)
	if err != nil {
		log.Fatalf("Warning: Unable to connect to database: %v\n", err)
	}
	defer repo.Pool.Close()

	apiInstance := &api.API{Repo: repo}

	r := chi.NewRouter()
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)

	apiInstance.MountRoutes(r)

	log.Println("Starting API server on :8080")
	http.ListenAndServe(":8080", r)
}
