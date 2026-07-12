export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  graphql_public: {
    Tables: {
      [_ in never]: never
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      graphql: {
        Args: {
          extensions?: Json
          operationName?: string
          query?: string
          variables?: Json
        }
        Returns: Json
      }
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
  public: {
    Tables: {
      edges: {
        Row: {
          created_at: string
          created_by: string | null
          notes: string | null
          relationship_type: Database["public"]["Enums"]["edge_type"]
          source_node_id: string
          strength_score: number
          target_node_id: string
          term_id: string | null
        }
        Insert: {
          created_at?: string
          created_by?: string | null
          notes?: string | null
          relationship_type?: Database["public"]["Enums"]["edge_type"]
          source_node_id: string
          strength_score?: number
          target_node_id: string
          term_id?: string | null
        }
        Update: {
          created_at?: string
          created_by?: string | null
          notes?: string | null
          relationship_type?: Database["public"]["Enums"]["edge_type"]
          source_node_id?: string
          strength_score?: number
          target_node_id?: string
          term_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "edges_source_node_id_fkey"
            columns: ["source_node_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "edges_target_node_id_fkey"
            columns: ["target_node_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "edges_term_id_fkey"
            columns: ["term_id"]
            isOneToOne: false
            referencedRelation: "terms"
            referencedColumns: ["id"]
          },
        ]
      }
      node_events: {
        Row: {
          actor: string | null
          created_at: string
          event_type: string
          id: number
          node_id: string
          payload: Json
        }
        Insert: {
          actor?: string | null
          created_at?: string
          event_type: string
          id?: never
          node_id: string
          payload?: Json
        }
        Update: {
          actor?: string | null
          created_at?: string
          event_type?: string
          id?: never
          node_id?: string
          payload?: Json
        }
        Relationships: [
          {
            foreignKeyName: "node_events_node_id_fkey"
            columns: ["node_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
        ]
      }
      nodes: {
        Row: {
          actionability: string | null
          assessed_at: string | null
          assessed_by: string | null
          category: Database["public"]["Enums"]["steep_category"]
          confidence_score: number | null
          convergence_score: number | null
          created_at: string
          created_by: string | null
          date_observed: string | null
          description: string
          embedding: string | null
          geography: string | null
          horizon_year: number | null
          id: string
          impact_score: number | null
          instructor_note: string | null
          is_keeper: boolean
          keeper_id: string | null
          mitigation_notes: string | null
          node_type: Database["public"]["Enums"]["node_type"]
          novelty_score: number | null
          polarity: Database["public"]["Enums"]["signal_polarity"]
          sector: string | null
          shadow_type: Database["public"]["Enums"]["shadow_type"] | null
          source_metadata: Json
          source_type: string | null
          source_url: string | null
          strategic_relevance: string | null
          tags: string[] | null
          term_id: string | null
          time_horizon: Database["public"]["Enums"]["horizon_type"]
          title: string
          uncertainty_score: number | null
          updated_at: string
          verification: Database["public"]["Enums"]["verification_status"]
        }
        Insert: {
          actionability?: string | null
          assessed_at?: string | null
          assessed_by?: string | null
          category: Database["public"]["Enums"]["steep_category"]
          confidence_score?: number | null
          convergence_score?: number | null
          created_at?: string
          created_by?: string | null
          date_observed?: string | null
          description: string
          embedding?: string | null
          geography?: string | null
          horizon_year?: number | null
          id?: string
          impact_score?: number | null
          instructor_note?: string | null
          is_keeper?: boolean
          keeper_id?: string | null
          mitigation_notes?: string | null
          node_type?: Database["public"]["Enums"]["node_type"]
          novelty_score?: number | null
          polarity?: Database["public"]["Enums"]["signal_polarity"]
          sector?: string | null
          shadow_type?: Database["public"]["Enums"]["shadow_type"] | null
          source_metadata?: Json
          source_type?: string | null
          source_url?: string | null
          strategic_relevance?: string | null
          tags?: string[] | null
          term_id?: string | null
          time_horizon: Database["public"]["Enums"]["horizon_type"]
          title: string
          uncertainty_score?: number | null
          updated_at?: string
          verification?: Database["public"]["Enums"]["verification_status"]
        }
        Update: {
          actionability?: string | null
          assessed_at?: string | null
          assessed_by?: string | null
          category?: Database["public"]["Enums"]["steep_category"]
          confidence_score?: number | null
          convergence_score?: number | null
          created_at?: string
          created_by?: string | null
          date_observed?: string | null
          description?: string
          embedding?: string | null
          geography?: string | null
          horizon_year?: number | null
          id?: string
          impact_score?: number | null
          instructor_note?: string | null
          is_keeper?: boolean
          keeper_id?: string | null
          mitigation_notes?: string | null
          node_type?: Database["public"]["Enums"]["node_type"]
          novelty_score?: number | null
          polarity?: Database["public"]["Enums"]["signal_polarity"]
          sector?: string | null
          shadow_type?: Database["public"]["Enums"]["shadow_type"] | null
          source_metadata?: Json
          source_type?: string | null
          source_url?: string | null
          strategic_relevance?: string | null
          tags?: string[] | null
          term_id?: string | null
          time_horizon?: Database["public"]["Enums"]["horizon_type"]
          title?: string
          uncertainty_score?: number | null
          updated_at?: string
          verification?: Database["public"]["Enums"]["verification_status"]
        }
        Relationships: [
          {
            foreignKeyName: "nodes_keeper_id_fkey"
            columns: ["keeper_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "nodes_term_id_fkey"
            columns: ["term_id"]
            isOneToOne: false
            referencedRelation: "terms"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          created_at: string
          full_name: string
          id: string
          is_approved: boolean
          role: Database["public"]["Enums"]["user_role"]
          term_id: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          full_name: string
          id: string
          is_approved?: boolean
          role?: Database["public"]["Enums"]["user_role"]
          term_id?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          full_name?: string
          id?: string
          is_approved?: boolean
          role?: Database["public"]["Enums"]["user_role"]
          term_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "profiles_term_id_fkey"
            columns: ["term_id"]
            isOneToOne: false
            referencedRelation: "terms"
            referencedColumns: ["id"]
          },
        ]
      }
      scenario_nodes: {
        Row: {
          created_at: string
          created_by: string | null
          node_id: string
          notes: string | null
          role: Database["public"]["Enums"]["scenario_node_role"]
          scenario_id: string
        }
        Insert: {
          created_at?: string
          created_by?: string | null
          node_id: string
          notes?: string | null
          role?: Database["public"]["Enums"]["scenario_node_role"]
          scenario_id: string
        }
        Update: {
          created_at?: string
          created_by?: string | null
          node_id?: string
          notes?: string | null
          role?: Database["public"]["Enums"]["scenario_node_role"]
          scenario_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "scenario_nodes_node_id_fkey"
            columns: ["node_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "scenario_nodes_scenario_id_fkey"
            columns: ["scenario_id"]
            isOneToOne: false
            referencedRelation: "scenarios"
            referencedColumns: ["id"]
          },
        ]
      }
      scenario_sets: {
        Row: {
          axis_x_high_label: string | null
          axis_x_low_label: string | null
          axis_x_node_id: string | null
          axis_y_high_label: string | null
          axis_y_low_label: string | null
          axis_y_node_id: string | null
          created_at: string
          created_by: string | null
          description: string | null
          horizon_year: number | null
          id: string
          is_published: boolean
          term_id: string | null
          title: string
          updated_at: string
        }
        Insert: {
          axis_x_high_label?: string | null
          axis_x_low_label?: string | null
          axis_x_node_id?: string | null
          axis_y_high_label?: string | null
          axis_y_low_label?: string | null
          axis_y_node_id?: string | null
          created_at?: string
          created_by?: string | null
          description?: string | null
          horizon_year?: number | null
          id?: string
          is_published?: boolean
          term_id?: string | null
          title: string
          updated_at?: string
        }
        Update: {
          axis_x_high_label?: string | null
          axis_x_low_label?: string | null
          axis_x_node_id?: string | null
          axis_y_high_label?: string | null
          axis_y_low_label?: string | null
          axis_y_node_id?: string | null
          created_at?: string
          created_by?: string | null
          description?: string | null
          horizon_year?: number | null
          id?: string
          is_published?: boolean
          term_id?: string | null
          title?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "scenario_sets_axis_x_node_id_fkey"
            columns: ["axis_x_node_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "scenario_sets_axis_y_node_id_fkey"
            columns: ["axis_y_node_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "scenario_sets_term_id_fkey"
            columns: ["term_id"]
            isOneToOne: false
            referencedRelation: "terms"
            referencedColumns: ["id"]
          },
        ]
      }
      scenarios: {
        Row: {
          created_at: string
          early_warning_indicators: string | null
          id: string
          narrative: string | null
          quadrant: Database["public"]["Enums"]["scenario_quadrant"]
          scenario_set_id: string
          title: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          early_warning_indicators?: string | null
          id?: string
          narrative?: string | null
          quadrant: Database["public"]["Enums"]["scenario_quadrant"]
          scenario_set_id: string
          title: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          early_warning_indicators?: string | null
          id?: string
          narrative?: string | null
          quadrant?: Database["public"]["Enums"]["scenario_quadrant"]
          scenario_set_id?: string
          title?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "scenarios_scenario_set_id_fkey"
            columns: ["scenario_set_id"]
            isOneToOne: false
            referencedRelation: "scenario_sets"
            referencedColumns: ["id"]
          },
        ]
      }
      terms: {
        Row: {
          created_at: string
          id: string
          invite_code: string
          is_active: boolean
          name: string
        }
        Insert: {
          created_at?: string
          id?: string
          invite_code: string
          is_active?: boolean
          name: string
        }
        Update: {
          created_at?: string
          id?: string
          invite_code?: string
          is_active?: boolean
          name?: string
        }
        Relationships: []
      }
      validations: {
        Row: {
          checklist: Json
          confidence: number
          created_at: string
          node_id: string
          note: string | null
          validator: string
        }
        Insert: {
          checklist: Json
          confidence: number
          created_at?: string
          node_id: string
          note?: string | null
          validator: string
        }
        Update: {
          checklist?: Json
          confidence?: number
          created_at?: string
          node_id?: string
          note?: string | null
          validator?: string
        }
        Relationships: [
          {
            foreignKeyName: "validations_node_id_fkey"
            columns: ["node_id"]
            isOneToOne: false
            referencedRelation: "nodes"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      current_user_is_approved: { Args: never; Returns: boolean }
      current_user_role: {
        Args: never
        Returns: Database["public"]["Enums"]["user_role"]
      }
      current_user_term_id: { Args: never; Returns: string }
      is_administrator: { Args: never; Returns: boolean }
      is_student: { Args: never; Returns: boolean }
      is_subscriber: { Args: never; Returns: boolean }
      surface_related_nodes: {
        Args: {
          match_count: number
          match_threshold: number
          target_embedding: string
        }
        Returns: {
          category: Database["public"]["Enums"]["steep_category"]
          id: string
          node_type: Database["public"]["Enums"]["node_type"]
          similarity: number
          title: string
        }[]
      }
    }
    Enums: {
      edge_type: "Cites" | "Consequence" | "Contradicts" | "Aggregates"
      horizon_type: "Near-term" | "Mid-term" | "Long-term"
      node_type:
        | "Signal"
        | "Shadow"
        | "Trend"
        | "Consequence-1"
        | "Consequence-2"
        | "Consequence-3"
      scenario_node_role:
        | "Driver"
        | "Evidence"
        | "Wildcard"
        | "Shadow-Risk"
        | "Implication"
      scenario_quadrant: "High-High" | "High-Low" | "Low-High" | "Low-Low"
      shadow_type:
        | "Declining-System"
        | "Obsolete-Behavior"
        | "Worst-Case-Future"
        | "Disruption"
      signal_polarity: "Emergent" | "Shadow"
      steep_category:
        | "Social"
        | "Technological"
        | "Economic"
        | "Environmental"
        | "Political"
        | "Legal"
      user_role: "Administrator" | "Student" | "Subscriber"
      verification_status: "Raw" | "Verified" | "Archived"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  graphql_public: {
    Enums: {},
  },
  public: {
    Enums: {
      edge_type: ["Cites", "Consequence", "Contradicts", "Aggregates"],
      horizon_type: ["Near-term", "Mid-term", "Long-term"],
      node_type: [
        "Signal",
        "Shadow",
        "Trend",
        "Consequence-1",
        "Consequence-2",
        "Consequence-3",
      ],
      scenario_node_role: [
        "Driver",
        "Evidence",
        "Wildcard",
        "Shadow-Risk",
        "Implication",
      ],
      scenario_quadrant: ["High-High", "High-Low", "Low-High", "Low-Low"],
      shadow_type: [
        "Declining-System",
        "Obsolete-Behavior",
        "Worst-Case-Future",
        "Disruption",
      ],
      signal_polarity: ["Emergent", "Shadow"],
      steep_category: [
        "Social",
        "Technological",
        "Economic",
        "Environmental",
        "Political",
        "Legal",
      ],
      user_role: ["Administrator", "Student", "Subscriber"],
      verification_status: ["Raw", "Verified", "Archived"],
    },
  },
} as const

