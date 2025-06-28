import { z } from "zod";

export const requestJobLogZodObject = z.object({
  type: z.enum(["info", "warn", "error"]),
  message: z.string(),
});
