import { defineCollection, z } from "astro:content";

const postSchema = z.object({
  title: z.string(),
  date: z.coerce.date(),
  tags: z.array(z.string()).optional(),
  categories: z.array(z.string()).optional(),
  description: z.string().optional(),
  draft: z.boolean().optional().default(false),
  latex_source: z.string().optional(),
  latex_pdf: z.string().optional()
});

const blog = defineCollection({
  type: "content",
  schema: postSchema
});

const musings = defineCollection({
  type: "content",
  schema: postSchema
});

const site = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string().optional(),
    description: z.string().optional()
  })
});

export const collections = { blog, musings, site };
