import java.io.*;
import java.net.*;
import java.nio.charset.StandardCharsets;
import java.util.Random;

/**
 * PollutionSensorSimulator
 * Generates random sensor values and POSTs them to the Flask server
 * every second as JSON — matching the /api/sensors endpoint format.
 *
 * Run this in Eclipse as a standard Java Application.
 * Make sure the Flask server (app.py) is running on localhost:5000 first.
 */
public class project {

    // Flask server URL
    private static final String SERVER_URL = "http://localhost:5000/api/sensors";

    // Update interval in milliseconds (1000 = 1 second, set to 0 for as fast as possible)
    private static final int INTERVAL_MS = 1000;

    private static final Random random = new Random();

    public static void main(String[] args) {
        System.out.println("=== Pollution Sensor Simulator ===");
        System.out.println("Sending data to: " + SERVER_URL);
        System.out.println("Press Ctrl+C to stop.\n");

        while (true) {
            try {
                // Generate random sensor values
                double temperature  = randomDouble(15.0, 45.0);   // °C
                double humidity     = randomDouble(20.0, 95.0);   // %
                int    mq135        = randomInt(50, 500);          // ppm (air quality)
                int    pm25         = randomInt(5, 250);           // µg/m³
                int    pm10         = pm25 + randomInt(5, 80);     // µg/m³ (always >= pm25)
                int    fc28         = randomInt(0, 100);           // % water tank level
                int    tds          = randomInt(100, 800);         // ppm water quality

                // Build JSON string matching Flask /api/sensors expected fields
                String json = String.format(
                    "{" +
                    "\"temperature\": %.1f," +
                    "\"humidity\": %.1f," +
                    "\"mq135\": %d," +
                    "\"pm25\": %d," +
                    "\"pm10\": %d," +
                    "\"fc28\": %d," +
                    "\"tds\": %d" +
                    "}",
                    temperature, humidity, mq135, pm25, pm10, fc28, tds
                );

                // Send POST request
                int statusCode = postJson(SERVER_URL, json);

                // Print to console
                System.out.printf(
                    "[SENT] Temp=%.1f°C  Hum=%.1f%%  MQ135=%dppm  PM2.5=%d  PM10=%d  FC28=%d%%  TDS=%dppm  → HTTP %d%n",
                    temperature, humidity, mq135, pm25, pm10, fc28, tds, statusCode
                );

                // Wait before next update
                if (INTERVAL_MS > 0) {
                    Thread.sleep(INTERVAL_MS);
                }

            } catch (InterruptedException e) {
                System.out.println("Stopped.");
                break;
            } catch (Exception e) {
                System.err.println("[ERROR] " + e.getMessage());
                try { Thread.sleep(2000); } catch (InterruptedException ie) { break; }
            }
        }
    }

    /**
     * Sends a JSON string via HTTP POST and returns the response status code.
     */
    private static int postJson(String urlStr, String json) throws IOException {
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
        conn.setDoOutput(true);
        conn.setConnectTimeout(3000);
        conn.setReadTimeout(3000);

        try (OutputStream os = conn.getOutputStream()) {
            byte[] input = json.getBytes(StandardCharsets.UTF_8);
            os.write(input, 0, input.length);
        }

        int status = conn.getResponseCode();
        conn.disconnect();
        return status;
    }

    private static double randomDouble(double min, double max) {
        return min + (max - min) * random.nextDouble();
    }

    private static int randomInt(int min, int max) {
        return min + random.nextInt(max - min + 1);
    }
}
