import express from "express";
import axios from "axios";
import fs from "fs";
import path from "path";
import cors from "cors";

export function createApp() {
  const app = express();

  const calculatorApi = process.env.CALCULATOR_API || "http://localhost:8001/calculate";
  const satelliteApi = process.env.SATELLITE_API || "http://localhost:8000/satellite";
  const rooftopApi = process.env.ROOFTOP_API || "http://localhost:8005/detect-rooftop";
  const nextApi = process.env.NEXT_API || "http://localhost:8007/generate-stl";

  const satelliteFolder = process.env.SATELLITE_FOLDER || path.resolve(process.cwd(), "satellite_images");
  const outputDir = process.env.OUTPUT_DIR || path.resolve(process.cwd(), "output_images");
  const corsOrigin = process.env.CORS_ORIGIN;

  fs.mkdirSync(satelliteFolder, { recursive: true });
  fs.mkdirSync(outputDir, { recursive: true });

  app.use(
    cors(
      corsOrigin
        ? {
            origin: corsOrigin.split(",").map((origin) => origin.trim()),
          }
        : undefined,
    ),
  );
  app.use(express.json());
  app.use("/output_images", express.static(outputDir));

  app.get("/", (req, res) => {
    res.json({
      message: "Backend proxy for Solar PV Calculator, Satellite & Rooftop API",
      forward_to: [calculatorApi, satelliteApi, rooftopApi],
    });
  });

  app.get("/health", (req, res) => {
    res.json({ status: "ok", service: "backend", uptime: process.uptime() });
  });

  app.post("/solar", async (req, res) => {
    try {
      const inputData = req.body;

      const calculatorPayload = {
        latitude: inputData.latitude,
        longitude: inputData.longitude,
        system_capacity_kw: inputData.system_capacity_kw,
        year: inputData.year,
        optimize_orientation: inputData.optimize_orientation,
        electricity_rate_inr: inputData.electricity_rate_inr,
        budget_inr: inputData.budget_inr,
        prefer_brand: inputData.prefer_brand,
        max_payback_years: inputData.max_payback_years,
      };

      const satellitePayload = {
        latitude: inputData.latitude,
        longitude: inputData.longitude,
        location_name: inputData.location_name || "unknown",
        zoom_level: inputData.zoom_level || 6,
      };

      const [calcResponse, satelliteResponse] = await Promise.all([
        axios.post(calculatorApi, calculatorPayload, { headers: { "Content-Type": "application/json" } }),
        axios.post(satelliteApi, satellitePayload, { headers: { "Content-Type": "application/json" } }),
      ]);

      const imageFiles = fs.readdirSync(satelliteFolder).filter((file) => {
        const ext = path.extname(file).toLowerCase();
        return ext === ".png" || ext === ".jpg" || ext === ".jpeg";
      });

      if (imageFiles.length === 0) {
        return res.status(404).json({ detail: "No images found in satellite_images folder" });
      }

      const savedImagePath = path.join(satelliteFolder, imageFiles[0]);

      const rooftopPayload = {
        image_path: savedImagePath,
        num_panels: calcResponse.data.system_configuration.modules_count,
      };

      const rooftopResponse = await axios.post(rooftopApi, rooftopPayload, {
        headers: { "Content-Type": "application/json" },
      });

      await axios.post(nextApi, null, {
        params: {
          roof_length: rooftopResponse.data.length,
          roof_width: rooftopResponse.data.width,
          num_panels: calcResponse.data.system_configuration.modules_count,
          tilt_angle: calcResponse.data.system_configuration.tilt_degrees,
        },
      });

      return res.status(200).json({
        success: true,
        message:
          "Combined response from Solar Calculator, Satellite API, Rooftop Detection, and Next API",
        calculator_result: calcResponse.data,
        satellite_result: satelliteResponse.data,
        rooftop_result: rooftopResponse.data,
      });
    } catch (error) {
      if (error.response) {
        return res.status(error.response.status).json({
          detail: `Error from remote API: ${error.response.statusText}`,
          data: error.response.data,
        });
      }

      if (error.request) {
        return res.status(504).json({
          detail: "No response received from one or more APIs",
          hint: "Ensure all remote APIs are running and reachable",
        });
      }

      return res.status(500).json({
        detail: "Internal proxy error",
        message: error.message,
      });
    }
  });

  return app;
}
