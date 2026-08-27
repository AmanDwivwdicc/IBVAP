export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.17"
  }
  public: {
    Tables: {
      alerts: {
        Row: {
          camera_id: string | null
          detection_count: number | null
          device_id: string | null
          evidence_path: string | null
          has_evidence: boolean | null
          id: string
          processed: boolean | null
          raw_payload: Json | null
          received_at: string | null
          timestamp: string
        }
        Insert: {
          camera_id?: string | null
          detection_count?: number | null
          device_id?: string | null
          evidence_path?: string | null
          has_evidence?: boolean | null
          id?: string
          processed?: boolean | null
          raw_payload?: Json | null
          received_at?: string | null
          timestamp: string
        }
        Update: {
          camera_id?: string | null
          detection_count?: number | null
          device_id?: string | null
          evidence_path?: string | null
          has_evidence?: boolean | null
          id?: string
          processed?: boolean | null
          raw_payload?: Json | null
          received_at?: string | null
          timestamp?: string
        }
        Relationships: [
          {
            foreignKeyName: "alerts_camera_id_fkey"
            columns: ["camera_id"]
            isOneToOne: false
            referencedRelation: "cameras"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "alerts_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "devices"
            referencedColumns: ["id"]
          },
        ]
      }
      anpr_results: {
        Row: {
          alert_id: string | null
          created_at: string | null
          detection_id: string | null
          id: string
          is_flagged: boolean | null
          plate_confidence: number | null
          plate_crop_path: string | null
          plate_text: string | null
        }
        Insert: {
          alert_id?: string | null
          created_at?: string | null
          detection_id?: string | null
          id?: string
          is_flagged?: boolean | null
          plate_confidence?: number | null
          plate_crop_path?: string | null
          plate_text?: string | null
        }
        Update: {
          alert_id?: string | null
          created_at?: string | null
          detection_id?: string | null
          id?: string
          is_flagged?: boolean | null
          plate_confidence?: number | null
          plate_crop_path?: string | null
          plate_text?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "anpr_results_alert_id_fkey"
            columns: ["alert_id"]
            isOneToOne: false
            referencedRelation: "alerts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "anpr_results_detection_id_fkey"
            columns: ["detection_id"]
            isOneToOne: false
            referencedRelation: "detections"
            referencedColumns: ["id"]
          },
        ]
      }
      audit_log: {
        Row: {
          action: string
          created_at: string | null
          details: Json | null
          id: string
          target_id: string | null
          target_type: string | null
          user_id: string | null
        }
        Insert: {
          action: string
          created_at?: string | null
          details?: Json | null
          id?: string
          target_id?: string | null
          target_type?: string | null
          user_id?: string | null
        }
        Update: {
          action?: string
          created_at?: string | null
          details?: Json | null
          id?: string
          target_id?: string | null
          target_type?: string | null
          user_id?: string | null
        }
        Relationships: []
      }
      cameras: {
        Row: {
          camera_id: string
          created_at: string | null
          device_id: string | null
          id: string
          is_active: boolean | null
          name: string | null
          source_url: string | null
        }
        Insert: {
          camera_id: string
          created_at?: string | null
          device_id?: string | null
          id?: string
          is_active?: boolean | null
          name?: string | null
          source_url?: string | null
        }
        Update: {
          camera_id?: string
          created_at?: string | null
          device_id?: string | null
          id?: string
          is_active?: boolean | null
          name?: string | null
          source_url?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "cameras_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "devices"
            referencedColumns: ["id"]
          },
        ]
      }
      detections: {
        Row: {
          alert_id: string | null
          bbox_xyxy: number[] | null
          class_id: number | null
          class_name: string | null
          confidence: number | null
          created_at: string | null
          feature: string
          id: string
          tracker_id: number | null
        }
        Insert: {
          alert_id?: string | null
          bbox_xyxy?: number[] | null
          class_id?: number | null
          class_name?: string | null
          confidence?: number | null
          created_at?: string | null
          feature: string
          id?: string
          tracker_id?: number | null
        }
        Update: {
          alert_id?: string | null
          bbox_xyxy?: number[] | null
          class_id?: number | null
          class_name?: string | null
          confidence?: number | null
          created_at?: string | null
          feature?: string
          id?: string
          tracker_id?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "detections_alert_id_fkey"
            columns: ["alert_id"]
            isOneToOne: false
            referencedRelation: "alerts"
            referencedColumns: ["id"]
          },
        ]
      }
      device_settings: {
        Row: {
          created_at: string | null
          created_by: string | null
          device_id: string | null
          id: string
          settings: Json
          version: string
        }
        Insert: {
          created_at?: string | null
          created_by?: string | null
          device_id?: string | null
          id?: string
          settings: Json
          version: string
        }
        Update: {
          created_at?: string | null
          created_by?: string | null
          device_id?: string | null
          id?: string
          settings?: Json
          version?: string
        }
        Relationships: [
          {
            foreignKeyName: "device_settings_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: true
            referencedRelation: "devices"
            referencedColumns: ["id"]
          },
        ]
      }
      devices: {
        Row: {
          api_key_hash: string | null
          coordinates: unknown
          created_at: string | null
          device_id: string
          id: string
          is_online: boolean | null
          last_seen_at: string | null
          location: string | null
          name: string | null
          settings_version: string | null
        }
        Insert: {
          api_key_hash?: string | null
          coordinates?: unknown
          created_at?: string | null
          device_id: string
          id?: string
          is_online?: boolean | null
          last_seen_at?: string | null
          location?: string | null
          name?: string | null
          settings_version?: string | null
        }
        Update: {
          api_key_hash?: string | null
          coordinates?: unknown
          created_at?: string | null
          device_id?: string
          id?: string
          is_online?: boolean | null
          last_seen_at?: string | null
          location?: string | null
          name?: string | null
          settings_version?: string | null
        }
        Relationships: []
      }
      face_results: {
        Row: {
          alert_id: string | null
          created_at: string | null
          detection_id: string | null
          face_crop_path: string | null
          face_embedding: string | null
          id: string
          matched_identity_id: string | null
          similarity_score: number | null
        }
        Insert: {
          alert_id?: string | null
          created_at?: string | null
          detection_id?: string | null
          face_crop_path?: string | null
          face_embedding?: string | null
          id?: string
          matched_identity_id?: string | null
          similarity_score?: number | null
        }
        Update: {
          alert_id?: string | null
          created_at?: string | null
          detection_id?: string | null
          face_crop_path?: string | null
          face_embedding?: string | null
          id?: string
          matched_identity_id?: string | null
          similarity_score?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "face_results_alert_id_fkey"
            columns: ["alert_id"]
            isOneToOne: false
            referencedRelation: "alerts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "face_results_detection_id_fkey"
            columns: ["detection_id"]
            isOneToOne: false
            referencedRelation: "detections"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "face_results_matched_identity_id_fkey"
            columns: ["matched_identity_id"]
            isOneToOne: false
            referencedRelation: "known_faces"
            referencedColumns: ["id"]
          },
        ]
      }
      known_faces: {
        Row: {
          created_at: string | null
          description: string | null
          face_embedding: string | null
          id: string
          name: string
          reference_image_path: string | null
          threat_level: string | null
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          face_embedding?: string | null
          id?: string
          name: string
          reference_image_path?: string | null
          threat_level?: string | null
        }
        Update: {
          created_at?: string | null
          description?: string | null
          face_embedding?: string | null
          id?: string
          name?: string
          reference_image_path?: string | null
          threat_level?: string | null
        }
        Relationships: []
      }
      watchlist_plates: {
        Row: {
          created_at: string | null
          description: string | null
          id: string
          plate_text: string
          threat_level: string | null
        }
        Insert: {
          created_at?: string | null
          description?: string | null
          id?: string
          plate_text: string
          threat_level?: string | null
        }
        Update: {
          created_at?: string | null
          description?: string | null
          id?: string
          plate_text?: string
          threat_level?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
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
  public: {
    Enums: {},
  },
} as const
